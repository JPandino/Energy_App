from flask import Flask, render_template, redirect, url_for, request, session
import uuid
import os
import numpy as np
import pandas as pd
import plotly.express as px
from optimization.milp import milp_optimization

app = Flask(__name__)
app.secret_key = 'supersecretkey'

@app.route("/", methods=['GET', 'POST'])
def index():
    if request.method == 'POST':

        session_id = str(uuid.uuid4())
        session['session_id'] = session_id

        upload_folder = os.path.join('uploads', session_id)
        os.makedirs(upload_folder, exist_ok=True)

        database_file = request.files['database_file']
        data = pd.read_csv(database_file)

        param1 = float(request.form['param1'])
        param2 = float(request.form['param2'])
        param3 = float(request.form['param3'])
        param4 = float(request.form['param4'])
        param5 = float(request.form['param5'])
        param7 = float(request.form['param7'])
        param11 = float(request.form['param11'])
        param13 = float(request.form['param13'])
        param15 = float(request.form['param15'])
        param16 = float(request.form['param16'])
        param17 = float(request.form['param17'])
        param18 = float(request.form['param18'])
        param19 = float(request.form['param19'])

        dic = {
            "param_1": param1,
            "param_2": param2,
            "param_3": param3,
            "param_4": param4,
            "param_5": param5,
            "param_7": param7,
            "param_11": param11,
            "param_13": param13,
            "param_15": param15,
            "param_16": param16,
            "param_17": param17,
            "param_18": param18,
            "param_19": param19
            }

        result, df_result = milp_optimization(dic, data)
        receita = round(result["Receita"], 2)

        data_path = os.path.join(upload_folder, 'temp_data1.csv')
        data.to_csv(data_path, index=False)

        dic = pd.DataFrame.from_dict(dic, orient='index')
        dic = dic.transpose()
        dic_path = os.path.join(upload_folder, 'temp_data2.csv')
        dic.to_csv(dic_path, index=False)

        df_result.index.name = 'time'
        result_path = os.path.join(upload_folder, 'temp_data3.csv')
        df_result.to_csv(result_path, index=True)

        return redirect(url_for('results', receita=receita, session_id=session_id))

    return render_template('index.html')

@app.route("/results", methods=['GET'])
def results():
    receita = request.args.get('receita')
    session_id = request.args.get('session_id')

    download_folder = os.path.join('uploads', session_id)
    data_path = os.path.join(download_folder, 'temp_data1.csv')
    data = pd.read_csv(data_path)

    dic_path = os.path.join(download_folder, 'temp_data2.csv')
    dic = pd.read_csv(dic_path)

    result_path = os.path.join(download_folder, 'temp_data3.csv')
    df_result = pd.read_csv(result_path)

    fig_1 = px.bar(data, y=data['upper_flow'], color_discrete_sequence=["magenta"])
    fig_1.update_layout(
        xaxis_title='horas',
        yaxis_title='Vazão (m³/s)',
        autosize=False,
        width=400,
        height=300
    )

    fig_2 = px.bar(data, y=data['lower_flow'], color_discrete_sequence=["goldenrod"])
    fig_2.update_layout(
        xaxis_title='horas',
        yaxis_title='Vazão (m³/s)',
        autosize=False,
        width=400,
        height=300
    )
    fig_3 = px.bar(data, y=data['pld'], color_discrete_sequence=["green"])
    fig_3.update_layout(
        xaxis_title='horas',
        yaxis_title='PLD (R$/MWh)',
        autosize=False,
        width=400,
        height=300
    )

    var_decisao = {}
    lista_variaveis = ["p", "pw", "vs", "qs", "vi", "qi", "i_p", "i_pw", "i_f", "i_p_pw", "i_pw_p", "i_os", "i_off"]

    for i in lista_variaveis:
        var_decisao[i] = []

    var_decisao["p"] = df_result["p"].apply(eval).tolist()
    var_decisao["pw"] = df_result["pw"].apply(eval).tolist()
    var_decisao["vs"] = df_result["vs"].tolist()
    var_decisao["qs"] = df_result["qs"].tolist()
    var_decisao["vi"] = df_result["vi"].tolist()
    var_decisao["qi"] = df_result["qi"].tolist()
    var_decisao["i_p"] = df_result["i_p"].apply(eval).tolist()
    var_decisao["i_pw"] = df_result["i_pw"].apply(eval).tolist()
    var_decisao["i_f"] = df_result["i_f"].tolist()
    var_decisao["i_p_pw"] = df_result["i_p_pw"].apply(eval).tolist()
    var_decisao["i_pw_p"] = df_result["i_pw_p"].apply(eval).tolist()
    var_decisao["i_os"] = df_result["i_os"].apply(eval).tolist()
    var_decisao["i_off"] = df_result["i_off"].apply(eval).tolist()

    # Vazões turbinada e bombeada das máquinas somadas
    flow_turbine_total = [sum(sublista) for sublista in var_decisao["p"]]
    flow_pump_total = [sum(sublista) for sublista in var_decisao["pw"]]
    fig_4 = px.bar(pd.DataFrame({'Vazão Turbinada': flow_turbine_total, 'Vazão Bombeada': flow_pump_total}))
    fig_4.update_layout(
        xaxis_title='Horizonte de Planejamento (horário)',
        yaxis_title='Vazão (m³/s)',
        autosize=False,
        width=1000,
        height=500,
    )

    # Tempo de operação das máquinas
    time_work = sum(var_decisao["i_f"])
    time_turbine = [sum(grupo) for grupo in zip(*var_decisao["i_p"])]
    tt1, tt2 = time_turbine
    tt = sum(time_turbine)
    time_pump = [sum(grupo) for grupo in zip(*var_decisao["i_pw"])]
    tp1, tp2 = time_pump
    tp = sum(time_pump)
    operation_data = dict(
        character=["work", "turbine", "pump", "turb_1", "turb_2", "pump_1", "pump_2"],
        parent=["", "work", "work", "turbine", "turbine", "pump", "pump"],
        value=[(time_work / 48) * 100, (tt / 48) * 100, (tp / 48) * 100, (tt1 / 48) * 100, (tt2 / 48) * 100,
               (tp1 / 48) * 100, (tp2 / 48) * 100])

    fig_5 = px.sunburst(
        operation_data,
        names='character',
        parents='parent',
        values='value'
    )

    fig_6 = px.line(df_result, y=['vs', 'vi'])
    fig_6.update_layout(
        xaxis_title='Horizonte de Planejamento (horário)',
        yaxis_title='Volume (hm³)',
        autosize=False,
        width=1000,
        height=500,
    )

    fig_7 = px.line(df_result, y=['qs', 'qi'])
    fig_7.update_layout(
        xaxis_title='Horizonte de Planejamento (horário)',
        yaxis_title='Vertimentos (m³/s)',
        autosize=False,
        width=1000,
        height=500,
    )

    flow_turbine_unit = [[sublista[i] for sublista in var_decisao["p"]] for i in range(2)]
    energy_turbine_unit = [[flow_turbine_unit[i][t] * dic["param_15"][0] for t in range(24)] for i in range(2)]
    energy_turbine_total = [sum(x) for x in zip(*energy_turbine_unit)]
    profit_spot = [(energy_turbine_total[t] - dic["param_18"][0]) * data["pld"][t] for t in range(24)]
    profit_acl = np.full(24, dic["param_18"][0] * dic["param_19"][0])

    fig_8 = px.line(pd.DataFrame({'Receita MCP': profit_spot, 'Receita ACL': profit_acl}))
    fig_8.update_layout(
        xaxis_title='Horizonte de Planejamento (horário)',
        yaxis_title='Receita (R$)',
        autosize=False,
        width=1000,
        height=500,
    )

    return render_template('results.html',
                           receita=receita,
                           plot_1=fig_1.to_html(),
                           plot_2=fig_2.to_html(),
                           plot_3=fig_3.to_html(),
                           plot_4=fig_4.to_html(),
                           plot_5=fig_5.to_html(),
                           plot_6=fig_6.to_html(),
                           plot_7=fig_7.to_html(),
                           plot_8=fig_8.to_html())

if __name__ == '__main__':
    app.run(debug=True)
