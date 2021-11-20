import numpy as np
import pandas as pd
import streamlit as st
import base64


#Title
st.title("TesserACT Patch Editor")
st.subheader("Please ensure that you enter the values for your first and last source line number before uploading a text file")
st.subheader("If you are fixing multiple geometries, please ensure that you type your source line information before uploading your next file")
#Adding a sidebar
st.sidebar.subheader("Data Uploader")


nlines = st.sidebar.slider("Number of Source Lines per Patch",
                           min_value=3,max_value=4,value=4)

st.sidebar.subheader("This information is available on your TesserACT design tab")
min_sl = st.sidebar.number_input("Lowest Source Line Number i.e 2.1, you have to input that format with a .1",
                                 step=0.1,format='%f')
max_sl = st.sidebar.number_input("Largest Source Line Number i.e 240.1, you have to input that format with a .1",
                                 step=0.1,format='%f')

direction = st.sidebar.selectbox('Do you have a decreasing number of source lines',('Yes','No'))


uploaded_file= st.sidebar.file_uploader(label="Upload your .txt file",
                         type=['txt'])

if uploaded_file is not None:
    df_init = pd.read_table(uploaded_file)

    patches = len(df_init.Patch.unique())
    source_lines = df_init[df_init.Type == "Source"]
    ## Creating a 62 x 4 array
    array = np.arange(min_sl, max_sl + 1, step=1)
    array_list = [i for i in array]


    if direction == "Yes":
        input_list = list(reversed(array_list))
    else:
        input_list = array_list

    dict_l = {i: "" for i in range(1, patches + 1)}

    # Code to populate dataframe
    start = 0
    end = 4
    for i in dict_l:
        dict_l[i] = input_list[start:end]
        start = start + 4
        end = end + 4

    df = pd.DataFrame({k: [v] for k, v in dict_l.items()}).astype(str)
    df = df.stack().reset_index(drop=True)
    print(df.tail(15))
    for i in range(len(df)):
        df[i] = df[i].replace('[', '')
        df[i] = df[i].replace(']', '')
        df[i] = df[i].replace(' ','')

    result = pd.Series(df).to_frame()
    result_df = result[result[0] != ""]
    result_df['Patch'] = [i for i in range(1, len(result_df) + 1)]
    result_df['Type'] = 'Source'
    result_df = result_df.rename(columns={0: 'Line Name'})
    export = result_df[['Patch', 'Type', 'Line Name']]
    export_df = export.append(df_init[df_init.Type =="Receiver"],ignore_index=True)
    export_df.to_csv('patch4.txt', sep='\t',index=False)

    @st.cache
    def convert_df(df):
        return df.to_csv(sep='\t',index=False).encode('utf-8')
    txt_file = convert_df(export_df)

    col1, col2 = st.columns(2)
    col1.header("Original Version")
    col1.write(df_init)

    col2.header('Edited Version')
    col2.write(export_df)

    st.download_button(label='Download File',data=txt_file, file_name='patch_edited.txt',mime='text/csv')