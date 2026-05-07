import streamlit as st
import pandas as pd
import numpy as np

by_def_enc = [ 'koi8_r']

if "encodings" not in st.session_state:
    st.session_state["encodings"] = by_def_enc #'utf-8', 'cp1251',
if "separs" not in st.session_state:
    st.session_state["separs"] =  [',', ';', '\t', ' ']
if "file" not in st.session_state:
    st.session_state["file"] = None
if "cur_level" not in st.session_state:
    st.session_state["cur_level"] = None
if "state" not in st.session_state:
    st.session_state["state"] = 'начальное'
if "param_load" not in st.session_state:
    st.session_state["param_load"] = None
if "df" not in st.session_state:
    st.session_state["df"] = None
if "params" not in st.session_state:
    st.session_state["params"] = None
if "sel_col" not in st.session_state:
    st.session_state["sel_col"] = None
if "ch_type_col" not in st.session_state:
    st.session_state["ch_type_col"] = None
if "df_not_eq" not in st.session_state:
    st.session_state["df_not_eq"] = None
if "nom_col" not in st.session_state:
    st.session_state["nom_col"] = None
if "col_x" not in st.session_state:
    st.session_state["col_x"] = None
if "col_y" not in st.session_state:
    st.session_state["col_y"] = []
if "head_graf" not in st.session_state:
    st.session_state["head_graf"] = ''

header = [0, None]
LOG = True

def LOG(s):
    if LOG:
        print(s)

def select_param_table(file, cont, verbose=False):
# функция отображения возможных датафреймов с разными параметрами
    param = dict()
    df_t = None
    i = 0
    try:
        if file.name.endswith('.csv'):
            file.seek(0)
            encodings = st.session_state["encodings"]
            separs = st.session_state["separs"]
            for enc in encodings:
                for sep in separs:
                    for head in header:
                        try:
                            str_step = f'кодировка: {enc}; разделитель: "' + str('tab' if sep == '\t' else sep) + '"; заголовки: "' + str('None' if head is None else str(head)) + '"'
                            #st.write(str_step)
                            df_t = pd.read_csv(file, encoding=enc, sep=sep, header=head, nrows=3)
                            if df_t is not None:
                                if len(df_t.columns) > 1:
                                    str_step = f'{i} : ' + str_step
                                    with cont:
                                        st.write( str_step, df_t)
                                    param[str_step] = [enc, sep, head]
                                    i += 1
                                file.seek(0)
                                #break
                            else:
                                file.seek(0)
                        except UnicodeDecodeError:
                            file.seek(0)
                        except pd.errors.ParserError:
                            file.seek(0)
    except pd.errors.EmptyDataError:
        if verbose:
            st.error("Ошибка: Файл пустой")
    except Exception as e:
        if verbose:
            st.error(f"Неожиданная ошибка: {str(e)}")
    return param

@st.cache_data()
def make_df(file, param_df):
    file.seek(0)
    df_t = pd.read_csv(file, encoding=param_df[0], sep=param_df[1], header=param_df[2])
    return df_t

def print_sym(s):
    ret =''
    if s == '\t':
        ret = 'tab'
    elif s == ' ':
        ret = 'space'
    else:
        ret = s
    return '"' + ret + '"'

def calc_index(fnd_val, list_fnd):
    # вычисление индекса элемента в списке. Для сохранения выбранного ранее элемента
    i = 0
    if fnd_val is not None:
        LOG(f'{i} в {fnd_val}')
        for ind in list_fnd:
            if ind == fnd_val:
                break
            i+=1
    return i if i <= len(list_fnd) - 1 else 0

def to_text(x):
    # преобразует полученное значение к строке. в случае ошибки #ошибка
    try:
        n = str(x)
    except Exception as e:
        LOG(f'вход {x} ошибка: {str(e)}')
        n = '#ошибка'
    return n

def to_num(x):
    # преобразует полученное значение к числу. в случае ошибки None
    try:
        n = pd.to_numeric(x)
    except Exception as e:
        #LOG(f'вход {x} ошибка: {str(e)}')
        n = None
    return n

# инициализация данных для преобразования дат
day_first=[True, False]
year_first=[True, False]
list_param_date = {}
i = 0
for d in day_first:
    for y in year_first:
        list_param_date[i] = [d, y]
        i += 1

def to_date(x, num_var):
    # преобразует полученное значение к дате по формату. в случае ошибки None
    try:
        n = pd.to_datetime(x, dayfirst=list_param_date[num_var][0], yearfirst=list_param_date[num_var][1])
    except Exception as e:
                # LOG(f'вход {x} ошибка: {str(e)}')
        n = None
    # print(tmp)
    return n

def dif_date(x):
# сравнивает даты в строке датасета и если хоть одна отличается, возвращает TRUE
    if x[0] != x[1] or x[0] != x[2] or x[0] != x[3]:
        return True
    else :
        return False
type_func = {'Текст': to_text, 'Число': to_num, 'Дата': to_date} # справочник функций для преобразования  к другому типу данных

def is_qm(s):
# проверяет есть ли в строке хоть один из символов ' или " или другие
    qm = ['"', "'", '\t']
    for q in qm:
        if s.find(q) != -1:
            return True
    return False

def qm_in_columns(col):
# получает список столбцов, проверяет на наличие спец.символов и возвращает название столбцов если значение хоть в одном столбце есть
    ret = []
    for c in col:
        res = is_qm(c)
        if res:
            ret.append(c)
    return ret

# начало отображения
with st.sidebar:
    new_file = st.file_uploader("Загрузите файл для анализа", type=["csv"])
    if new_file != st.session_state.file:
        LOG(f'!!! {new_file} {st.session_state.file}')
        st.session_state["file"] = new_file
        st.session_state.state = 'начальное'
        st.session_state.cur_level = None
        st.session_state.sel_col = None

    lst_option=[]
    LOG(f'создание списка: {st.session_state.cur_level}:{st.session_state.state}')
    if st.session_state.state in ('начальное', 'add_cod'):
        lst_option.append('Загрузка данных')
    elif st.session_state.state in ('load_data', 'подг', 'mod_name', 'подтв', 'подтв_type', 'подтв_save'):
        lst_option.extend(['Загрузка данных', 'Предобработка данных'])
    elif st.session_state.state in ('confirm_data', 'visio_data'):
        lst_option.extend(['Загрузка данных', 'Предобработка данных', 'Графики'])

    i = calc_index(st.session_state.cur_level, lst_option)
    st.write('Обработка CSV файлов')
    LOG(f'{i} в {lst_option}')
    cur_level = st.selectbox('Этапы обработки', lst_option, index=i)
    LOG(f'L 1: {cur_level} -- {st.session_state.cur_level}')
    if cur_level != st.session_state.cur_level:
        LOG(f'L 2: {cur_level} -- {st.session_state.cur_level}')
        if st.session_state.cur_level is None:
            LOG(f'L 3: {cur_level} -- {st.session_state.cur_level} -- {st.session_state.state}')
            st.session_state.cur_level = cur_level
            st.session_state.state = 'начальное'
        else:
            LOG(f'L 4: {cur_level} -- {st.session_state.cur_level} -- {st.session_state.state}')
            st.session_state.cur_level = cur_level
            st.session_state.state = 'начальное'
    else:
        LOG(f'L 5: {cur_level} -- {st.session_state.cur_level} -- {st.session_state.state}')
        st.session_state.cur_level = cur_level

if st.session_state.cur_level == 'Загрузка данных':
    cont_set = st.container(border=True, horizontal_alignment="center")
    with cont_set:
        cont_cod =  st.container(border=True, horizontal_alignment="center")
    with cont_set:
        cont_sep = st.container(border=True, horizontal_alignment="center", horizontal=True)
    with cont_cod:
        cont_cod_lbl = st.container(horizontal_alignment="center", horizontal=True)
    cont_cod_lbl.write('доступные кодировки: ' + ', '.join(map( lambda x: '"' + x + '"', st.session_state["encodings"])))
    cod_add = cont_cod_lbl.button('+', key='btn_cod_add', help='добавить новую кодировку', disabled=st.session_state.state != 'начальное')
    cod_bydf = cont_cod_lbl.button('R', key='btn_cod_bydf', help='восстановить начальную кодировку',
                                  disabled=st.session_state.state != 'начальное')
    if cod_bydf:
        st.session_state["encodings"] = by_def_enc
        st.rerun()
    cont_sep.write('доступные разделители' + '\t'.join(map( print_sym, st.session_state["separs"])))
    if cod_add or st.session_state['state'] == 'add_cod':
        st.session_state.state = 'add_cod'
        with cont_cod:
            cont_cod_inp = st.container(horizontal_alignment="center", horizontal=True)
        cod_add_help = 'добавляемая кодировка без ""(задается только одно название за раз)'
        new_cod = cont_cod_inp.text_input('новая кодировка:',help=cod_add_help)
        cod_save = cont_cod_inp.button('V', key='btn_cod_save', help='Сохранить')
        cod_canc = cont_cod_inp.button('C', key='btn_cod_canc', help='Отмена')
        if cod_save:
            if len(new_cod) < 4:
                cont_cod_inp.error('короткое имя')
                st.stop()
            if new_cod in st.session_state["encodings"]:
                # проверка, что такой кодировки еще нет
                cont_cod_inp.error('такая кодировка уже есть')
                st.stop()
            st.session_state["encodings"].append(new_cod)
            st.session_state.state = 'начальное'
            st.rerun()
        if cod_canc:
            st.session_state.state = 'начальное'
            st.rerun()

    cont_file = st.container(border=True, horizontal_alignment="center")
    with cont_file:
        cont_fl_name = st.container(border=True, horizontal_alignment="center")
        cont_fl_ch = st.container(border=True, horizontal_alignment="center")
    if st.session_state.file is not None:
        if st.session_state.state != 'load_data':
            if LOG:
                print(f'3. перед расчетом {st.session_state.state}')
            st.session_state.params = select_param_table(st.session_state.file, cont_fl_ch, verbose=True)
            st.session_state.param_load = cont_fl_name.selectbox('Выберите из списка какие параметры загрузки использовать:', st.session_state.params.keys())
            if LOG:
                print(f'4. после отображения выбора списка:  {st.session_state.state}')
        btn_make = cont_fl_name.button("Применить выбранные параметры для загрузки всех данных", disabled=st.session_state.state != 'начальное')
        if LOG:
            print(f'5. значение кнопки{btn_make} -- {st.session_state.state}')
        if btn_make or st.session_state.state == 'load_data':
            st.session_state.state = 'load_data'
            if LOG:
                print(f'6. в условии:{btn_make} -- {st.session_state.state}')
            if btn_make:
                st.rerun()
            with cont_fl_ch:
                if LOG:
                    print(f'7. в условии:{btn_make} -- {st.session_state.state}')
                with st.spinner("Загрузка данных"):
                  #  LOG(f'----{st.session_state.file}"\n"{st.session_state.param_load}"\n"{st.session_state.params}')
                    st.session_state.df = make_df(st.session_state.file, st.session_state.params[st.session_state.param_load])
                st.success(f'Загружено: {st.session_state.df.shape[0]} строк; {st.session_state.df.shape[1]} столбцов')
                st.write(st.session_state.df.head(5))
                i = 0
                for col in st.session_state.df.columns:
                    str_out = f'N:{i} Столбец: {col}; Кол-во Null: {st.session_state.df[col].isnull().sum()}; Тип: {st.session_state.df[col].dtype}'
                    st.write(str_out)
                    i+=1
elif st.session_state.cur_level == 'Предобработка данных':
    if st.session_state.state in ('load_data', 'начальное'):
        st.session_state.col_y.clear()
        st.session_state.col_x = None
    st.session_state.state = 'подг' if st.session_state.state in ('load_data', 'начальное') else st.session_state.state
    cont_par = st.container(border=True, horizontal_alignment="center")
    with cont_par:
        cont_df = st.container(border=True, horizontal_alignment="center")
        cont_par_set = st.container(border=True, horizontal_alignment="center")
        with cont_par_set:
            cont_par_col = st.container(border=True, horizontal_alignment="center")
            cont_par_par = st.container(border=True, horizontal_alignment="center")
        with cont_df:
            col_qm = qm_in_columns(st.session_state.df.columns)
            if len(col_qm) > 0:
                st.warning(f'Внимание! В названиях столбцов ({', '.join(map( lambda x: '"' + x + '"', col_qm))}) есть специальные символы, которые могут повлиять на отображение графиков!')
            st.write(f'Таблица для предобработки. Кол-во строк: {st.session_state.df.shape[0]}')
            st.write(st.session_state.df)
            btn_end_mod = st.button('завершить преобразование', disabled=st.session_state.state in ('mod_name', 'подтв', 'подтв_type', 'подтв_save'))
            if st.session_state.state == 'confirm_data':
                cont_df.success('доступно построение графиков')
            if btn_end_mod:
                st.session_state.state = 'confirm_data'
                st.rerun()
        LOG(f'Перед индексом {st.session_state.sel_col} {st.session_state.df.columns}')
        i = calc_index(st.session_state.sel_col, st.session_state.df.columns)
        sel_col = cont_par_col.selectbox('Выбор столбца:', st.session_state.df.columns, index=i, disabled=st.session_state.state in ('mod_name', 'подтв', 'подтв_type', 'подтв_save'))
        st.session_state.sel_col = sel_col
        type_dat = cont_par_col.selectbox('Тип параметров столбца',['Название','Тип', 'Статистика'], disabled=st.session_state.state in ('mod_name', 'подтв', 'подтв_type', 'подтв_save'))
        with cont_par_col:
            cont_par_dat = st.container(border=True, horizontal_alignment="center", horizontal=True)
        if type_dat == 'Название':
            cont_par_dat.write('Текущее название:')
            cont_par_dat.write(sel_col)
            btn_mod_name = cont_par_dat.button('M', help='Изменить', disabled=st.session_state.state in ('mod_name', 'подтв', 'подтв_type', 'подтв_save'))
            LOG(f'кноп M= {btn_mod_name}; state={st.session_state.state}')
            if btn_mod_name:# or st.session_state.state in ('mod_name', 'подтв'):
                st.session_state.state = 'подтв'
                st.rerun()
            if st.session_state.state == 'подтв':
                new_name = cont_par_dat.text_input('Новое название:', value=sel_col)
                with cont_par_dat:
                    cont_par_btn = st.container(horizontal_alignment="center")
                btn_save = cont_par_btn.button('V', help='Сохранить', key='btn_save_name')
                LOG(f'кноп save press = {btn_save}; state={st.session_state.state}; new_name={new_name}')
                btn_canc = cont_par_btn.button('C', help='Отмена', key='btn_canc_name')
                LOG(f'кноп S= {btn_save}; state={st.session_state.state}; new_name={new_name}')
                if btn_save:
                    if len(new_name) < 1:
                        LOG(f'len < 1; кноп S= {btn_save}; state={st.session_state.state}; new_name={new_name}')
                        cont_par_dat.error('Название не может быть пустым')
                        st.stop()
                    if new_name in st.session_state.df.columns:
                        LOG(f'столб есть: кноп S = {btn_save}; state={st.session_state.state}; new_name={new_name}')
                        cont_par_dat.error('Такое название столбца уже используется')
                        st.stop()
                    with st.spinner("Переименование столбца..."):
                        st.session_state.df.rename(columns={sel_col: new_name}, inplace=True)
                    st.success("Переименование столбца - завершено")
                    st.session_state.sel_col = new_name
                    st.session_state.state = 'подг'
                    LOG(f'Save; state={st.session_state.state}; new_name={new_name}')
                    st.rerun()
                if btn_canc:
                    st.session_state.state = 'подг'
                    st.rerun()
        if type_dat == 'Тип':
            cont_par_dat.write('Текущий тип:')
            cont_par_dat.write(st.session_state.df[sel_col].dtype)
            btn_mod_name = cont_par_dat.button('M', help='Изменить', disabled=st.session_state.state in ('mod_name', 'подтв', 'подтв_type', 'подтв_save'))
            LOG(f'кноп M= {btn_mod_name}; state={st.session_state.state}')
            if btn_mod_name or st.session_state.state in ('mod_name', 'подтв', 'подтв_type', 'подтв_save'):
                st.session_state.state = 'mod_name' if st.session_state.state not in ('подтв', 'подтв_type', 'подтв_save') else st.session_state.state
                LOG(f'1-0 {btn_mod_name}; state={st.session_state.state}')
                new_type = cont_par_dat.selectbox('Новый тип:', ['Текст', 'Число', 'Дата'], disabled=st.session_state.state in ( 'подтв_type', 'подтв_save'))
                LOG(f'2-0 после выбора типа на что менять {btn_mod_name}; state={st.session_state.state} {new_type}')
                with cont_par_dat:
                    cont_par_btn = st.container(horizontal_alignment="center", horizontal=True)
                btn_test = cont_par_btn.button('T', help='Протестировать', key='btn_test_type', disabled=st.session_state.state in ('подтв', 'подтв_type', 'подтв_save'))
                btn_save = cont_par_btn.button('V', help='Сохранить', key='btn_save_type', disabled=st.session_state.state in ('mod_name'))
                btn_canc = cont_par_btn.button('C', help='Отмена', key='btn_canc_type')
                if btn_test or st.session_state.state in ('подтв', 'подтв_type', 'подтв_save'):
                    LOG(f'3-0 {btn_mod_name}; state={st.session_state.state} {new_type}')
                    if new_type == 'Текст' and st.session_state.state != 'подтв':
                        with st.spinner("Конвертация столбца к текстовому типу"):
                            st.session_state.ch_type_col = st.session_state.df[sel_col].map(to_text)
                        st.success("Конвертация столбца к текстовому типу - завершено")
                        st.session_state.state = 'подтв'
                        st.rerun()
                    elif new_type == 'Число' and st.session_state.state != 'подтв':
                        with st.spinner("Конвертация столбца к числовому типу"):
                            st.session_state.ch_type_col = st.session_state.df[sel_col].map(to_num)
                        st.success("Конвертация столбца к числовому типу - завершено")
                        st.session_state.state = 'подтв'
                        st.rerun()
                    elif new_type == 'Дата' and st.session_state.state not in ('подтв'):
                        LOG(f'1. {new_type}; state={st.session_state.state}')
                        if st.session_state.state not in ('подтв_type', 'подтв_save'):
                            with st.spinner("анализ значений столбца"):
                                df_lst = pd.DataFrame()
                                df_lst['вх'] = st.session_state.df[sel_col].head(2000)
                                for ind in list_param_date.keys():
                                    tmp = st.session_state.df[sel_col].head(2000).map(lambda x: to_date(x, num_var=ind))
                                    df_lst[ind] = tmp
                                df_lst['not equal'] = df_lst.apply(dif_date, axis=1)
                                st.session_state.df_not_eq = df_lst[df_lst['not equal']]
                                if st.session_state.df_not_eq.shape[0] > 0:
                                    LOG(f'2. Больше 0. {new_type}; state={st.session_state.state}')
                                    st.session_state.state = 'подтв_type'
                                else:
                                    LOG(f'3. 0. {new_type}; state={st.session_state.state}')
                                    st.session_state.state = 'подтв_type'
                                st.rerun()
                        elif st.session_state.state in ('подтв_type'):
                            LOG(f'4. {new_type}; state={st.session_state.state}')
                            if st.session_state.df_not_eq.shape[0] > 0:
                                LOG(f'5. больше 0. {new_type}; state={st.session_state.state}')
                                str = f'''В списке укажите название столбца, который соответствует нужному формату'''
                                cont_par_par.write(str)
                                st.session_state.state = 'подтв_save'
                                LOG(f'6. стопим {new_type}; state={st.session_state.state}')
                                st.rerun()
                            else:
                                LOG(f'4-0 {btn_mod_name}; state={st.session_state.state} {new_type}')
                                LOG(f'сохранение временного столбца {sel_col}')
                                st.session_state.ch_type_col = st.session_state.df[sel_col].map(lambda x: to_date(x, num_var=0))
                                st.success("Конвертация столбца к Дате - завершено")
                                LOG(f'4-1 Сохранили вр столб {btn_mod_name}; state={st.session_state.state} {new_type}')
                                st.session_state.state = 'подтв'
                                st.rerun()
                        elif st.session_state.state == 'подтв_save':
                            LOG(f'4-1 подтверидть {btn_mod_name}; state={st.session_state.state} {new_type}')
                            str = f'''Найдены даты для которых необходимо указать тип 
                                        преобразования ЯВНО.\nВ списке укажите название столбца, который соответствует нужному формату'''
                            cont_par_par.write(str)
                            st.session_state.nom_col = cont_par_par.selectbox('', list_param_date.keys())
                            LOG(f'5.2 Выбран {st.session_state.nom_col}')
                            cont_par_par.write(st.session_state.df_not_eq)
                    if st.session_state.state != 'подтв_save' and st.session_state.state != 'подтв_save':
                        LOG(f'5-0 {btn_mod_name}; state={st.session_state.state} {new_type}')
                        cont_par_par.write('статистика:')
                        if st.session_state.state == 'подтв_save':
                            st.session_state.nom_col = cont_par_par.selectbox('', list_param_date.keys())
                            LOG(f'5-2 Выбран {st.session_state.nom_col}')
                        with st.spinner(f'получение статистики. Столбец: {st.session_state.nom_col}'):
                            if st.session_state.state == 'подтв_save':
                                cnt_val = st.session_state.df[sel_col].map(lambda x: to_date(x, num_var=st.session_state.nom_col)).value_counts()
                            else:
                                cnt_val = st.session_state.ch_type_col.value_counts()
                            cont_par_par.write(cnt_val.sort_values(ascending=False))
                if btn_save:
                    LOG(f'клик Save {new_type} {st.session_state.state}: {st.session_state.nom_col}')
                    if new_type != 'Дата':
                        with st.spinner("Итоговая конвертация столбца"):
                            st.session_state.df[sel_col] = st.session_state.df[sel_col].map(type_func[new_type])
                            st.success("Итоговая конвертация столбца - завершено")
                    with cont_par_btn:
                        with st.spinner(f"Итоговая конвертация столбца {st.session_state.nom_col}"):
                            if new_type == 'Дата':
                                LOG('в дате')
                                if st.session_state.state == 'подтв_save':
                                    LOG(f'{st.session_state.state}')
                                    st.session_state.df[sel_col] = st.session_state.df[sel_col].map(lambda x: to_date(x, num_var=st.session_state.nom_col))
                                else:
                                    LOG('else')
                                    st.session_state.df[sel_col] = st.session_state.df[sel_col].map(lambda x: to_date(x, num_var=0))
                        st.success("Итоговая конвертация столбца - завершено")
                    st.session_state.state = 'подг'
                    st.session_state.ch_type_col = None
                    st.rerun()
                if btn_canc:
                    st.session_state.state = 'подг'
                    st.session_state.ch_type_col = None
                    st.rerun()
        if type_dat == 'Статистика':
            str_out = f'Тип данных: {st.session_state.df[sel_col].dtype}'
            cont_par_dat.write(str_out)
            str_out = f'Уникальных значений: {st.session_state.df[sel_col].unique().shape[0]}'
            cont_par_dat.write(str_out)
            str_out = f'Nan значений: {st.session_state.df[st.session_state.df[sel_col].isnull()].shape[0]}'
            cont_par_dat.write(str_out)
            str_out = f'Минимальное значение: {st.session_state.df[sel_col].min(numeric_only=True)}'
            cont_par_dat.write(str_out)
            str_out = f'Максимальное значение: {st.session_state.df[sel_col].max(numeric_only=True)}'
            cont_par_dat.write(str_out)
            if st.session_state.df[sel_col].dtype != 'str':
                str_out = f'Среднее значение: {st.session_state.df[sel_col].mean(numeric_only=True)}'
                cont_par_dat.write(str_out)
                str_out = f'Медианное значение: {st.session_state.df[sel_col].median(numeric_only=True)}'
                cont_par_dat.write(str_out)
                str_out = f'среднеквадратичное отклонение: {st.session_state.df[sel_col].std(numeric_only=True)}'
                cont_par_dat.write(str_out)
            with cont_par_col:
                cont_par_top = st.container(horizontal_alignment="center")
            str_out = f'Топ 10 частых значений'
            cont_par_top.write(str_out)
            cont_par_top.write(st.session_state.df[sel_col].value_counts().sort_values(ascending=False).head(10))
            str_out = f'Топ 10 редких значений'
            cont_par_top.write(str_out)
            cont_par_top.write(st.session_state.df[sel_col].value_counts().sort_values().head(10))
elif st.session_state.cur_level == 'Графики':
    LOG(f'старт графики {st.session_state.state}')
    if st.session_state.state in ('начальное', 'confirm_data'):
        st.session_state.col_x = None
        st.session_state.col_y = []
        st.session_state.head_graf = ''
    st.session_state.state = 'visio_data' if st.session_state.state in ('начальное', 'confirm_data') else st.session_state.state
    cont_gr_head = st.container( horizontal_alignment="center")
    cont_gr = st.container(border=True, horizontal_alignment="center")
    with cont_gr_head:
        cont_gr_txt = st.container( horizontal_alignment="center", horizontal=True)
        cont_gr_par = st.container(border=True, horizontal_alignment="center") #, horizontal=True)
    cont_gr_txt.write('Построение графиков')
    type_gr = cont_gr_par.selectbox('Укажите тип графика: ', ['Линейный','Рассеяния','Столбчатый'])
    LOG(f'выбрали график {type_gr} {st.session_state.state}')
    if type_gr == 'Линейный':
        max_y = 0
    elif type_gr == 'Столбчатый':
        max_y = 0
    elif type_gr == 'Рассеяния':
        max_y = 0
    x_col =[] # формирую список столбцов для оси Х. (не входящих с список по оси Y)
    if type_gr in ('Линейный', 'Рассеяния'):
        for c_x in st.session_state.df.select_dtypes(include=['number', 'datetime64']).columns:
            if c_x not in st.session_state.col_y:
                x_col.append(c_x)
    else:
        for c_x in st.session_state.df.columns:
            if c_x not in st.session_state.col_y:
                x_col.append(c_x)
    x_list = cont_gr_par.selectbox('столбец по оси Х:', x_col, index=calc_index(st.session_state.col_x, x_col))
    st.session_state.col_x = x_list
    x_title = cont_gr_par.text_input('Подпись к оси X:')
    y_col = []  # формирую список столбцов для оси Y. (не входящих с список по оси X)
    for c_y in st.session_state.df.select_dtypes(include=np.number).columns:
        if c_y not in x_list:
            if c_y not in st.session_state.col_y:
                y_col.append(c_y)
    cont_gr_par.write(f'Для отображения по оси Y выбраны столбцы: {', '.join(map( lambda x: '"' + x + '"', st.session_state.col_y))}')
    if len(st.session_state.col_y) == 0:
        cont_gr_par.warning('столбцы по У не выбраны')
    cont_gr_par_y = cont_gr_par.container(horizontal_alignment="center", horizontal=True)
    y_list = cont_gr_par_y.selectbox('Выберите столбец/ы отображаемый по оси Y:', y_col)
    btn_add = cont_gr_par_y.button('+', help='Добавить столбец в список столбцов по оси Y')
    btn_clear = cont_gr_par_y.button('C', help='Очистить список столбцов по оси Y')
    y_title = cont_gr_par.text_input('Подпись к оси Y:')
    st.session_state.head_graf = cont_gr_par.text_input('Заголовок графика:', value=st.session_state.head_graf)
    cont_gr_par_ch = cont_gr_par.container(horizontal_alignment="center", horizontal=True)
    ch_filter = cont_gr_par_ch.checkbox('Использовать фильтр')
    if ch_filter:
        cont_gr_par_fil = cont_gr_par.container(horizontal_alignment="center", horizontal=True)
        filt_col = cont_gr_par_fil.selectbox('Фильтруемый столбец:', st.session_state.df.columns)
        fil_value = cont_gr_par_fil.selectbox('Укажите значение:', st.session_state.df[filt_col].unique())
    ch_oper = cont_gr_par.checkbox('Операция над значениями по Y')
    if ch_oper:
            ch_type = cont_gr_par.radio( '', ['Суммировать', 'Среднее'], horizontal=True)
    btn_show = cont_gr_par.button('Показать график')
    if btn_add:
        if y_list in st.session_state.col_y:
            cont_gr_par.error('Такой столбец уже присутствует в списке')
            st.stop()
        elif max_y > 0 and len(st.session_state.col_y) >= max_y:
            cont_gr_par.error('Для данного вида графика достигнуто максимальное значение столбцов')
            st.stop()
        else:
            st.session_state.col_y.append(y_list)
            st.rerun()
    if btn_clear:
        st.session_state.col_y.clear()
        st.rerun()
    if len(st.session_state.col_y) == 0:
        st.stop()
    if btn_show:
        # проверка, что все поля заполнены
        LOG('Проверка заполненности полей')
        if st.session_state.col_x is None or len(st.session_state.col_x) == 0 or len(x_title) == 0 or len(y_title) == 0 or len(st.session_state.head_graf) == 0:
            LOG('не все поля')
            cont_gr_par.warning('Указаны не все поля')
            st.stop()
        with cont_gr_par.spinner('Построение графика'):
        # расчет дата фрейма и настройка графика
            col_gr = []
            col_gr.append(st.session_state.col_x)
            col_gr.extend(st.session_state.col_y)
            LOG(f'Список столбцов: {col_gr} х={st.session_state.col_x}  y={st.session_state.col_y}')
            if ch_filter:
                if not ch_oper:
                    df_gr = st.session_state.df.loc[st.session_state.df[filt_col] == fil_value, col_gr]
                else:
                    df_gr = st.session_state.df.loc[st.session_state.df[filt_col] == fil_value, col_gr].groupby(
                        st.session_state.col_x, as_index=False)[st.session_state.col_y].sum()
            else:
                if not ch_oper:
                    df_gr = st.session_state.df[col_gr]
                else:
                    if ch_type == 'Суммировать':
                        df_gr = st.session_state.df[col_gr].groupby(st.session_state.col_x, as_index=False)[
                            st.session_state.col_y].sum()
                    elif ch_type == 'Среднее':
                        df_gr = st.session_state.df[col_gr].groupby(st.session_state.col_x, as_index=False)[
                            st.session_state.col_y].mean()
            str_title = ''
            if len(st.session_state.head_graf) > 0:
                str_title = st.session_state.head_graf
            if ch_filter:
                str_title = f'{str_title}  для {filt_col} имееющему значение "{fil_value}"'
            if ch_oper:
                if ch_type == 'Суммировать':
                    ch_str = 'просуммированы'
                elif ch_type == 'Среднее':
                    ch_str = 'среднее значение'
                str_title = f'{str_title}. (данные по оси Y {ch_str})'
        # построение графика
            LOG('построить график')
            cont_gr_title = cont_gr.container(horizontal_alignment="center", horizontal=True)
            cont_gr_title.write(str_title)
            LOG(f'строк в датафрейме {len(df_gr)}')
            try:
                if type_gr == 'Линейный':
                    with cont_gr.spinner('Отображение графика'):
                        cont_gr.line_chart(df_gr, x=st.session_state.col_x, y=st.session_state.col_y, x_label=x_title, y_label=y_title)
                elif type_gr == 'Столбчатый':
                    with cont_gr.spinner('Отображение графика'):
                        cont_gr.bar_chart(df_gr,  x=st.session_state.col_x, y=st.session_state.col_y, x_label=x_title, y_label=y_title)
                elif type_gr =='Рассеяния':
                    with cont_gr.spinner('Отображение графика'):
                        cont_gr.scatter_chart(df_gr, x=st.session_state.col_x, y=st.session_state.col_y, x_label=x_title, y_label=y_title)
            except Exception as e:
                LOG(e)
                cont_gr.error('Постройка данного типа графика с указанными параметрами не возможна! Попробуйте другие параметры.')
            cont_gr_par.success(f'График построен. Строк для отображения {len(df_gr)}. Если график не отображается, проверьте наличие в названиях столбцов кавычек и др.спец. символов')
