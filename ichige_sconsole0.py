import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import japanize_matplotlib

st.title('イチゲブログのGoogle Search Console検索データ分析')
st.caption('イチゲブログのGoogle Search Consoleで検索データを月ごとにExcelで取り出し表示できるようにしました。クエリを2つ選んで月ごとの検索順位が分かります。')
st.markdown('###### 詳細は')
link = '[イチゲブログ](https://kikuichige.com/17288/)'
st.markdown(link, unsafe_allow_html=True)

#ichige_sconsole.csvをデータフレームで開く
df = pd.read_csv('ichige_sconsole.csv')
#st.text_inputの第一引数-ラベル、第二引数-初期値
query_name=st.text_input('検索したいワード')
#st.form内のデータはsubmit_btnが押されると更新される。keyは、このフォームの名前で何でもいい。
with st.form(key='profile_form'):
#セレクトボックス今回はマルチセレクトにした。
#上位クエリと掲載順位だけのデータフレームを作り掲載順位の最小値を抽出
    df_value_min = df[['上位のクエリ','掲載順位']].groupby('上位のクエリ').min()
    #掲載順位昇順で並べ替え
    f_s = df_value_min.sort_values('掲載順位')
    #index（上位のクエリ）の一覧作成。indexがarray型なのでtolistでlist化
    query_list=f_s.index.values.tolist()
    #検索したいワードに値がある場合は、その値が含まれるクエリのみにする。
    l_in = [s for s in query_list if query_name in s]
    #セレクトボックス初期値空欄に設定
    l_in.insert(0, '-')
    # selected_query=st.selectbox('クエリ候補(検索したいワードに入力してEnterすると候補が選択できます。▽をクリック！）',l_in[:100])
 #マルチセレクト
    mul_sel=st.multiselect(
            '▼をクリック！全区間で平均検索順位の高い順に２００個表示されます。2つ選んでください。(検索したいワードに入力してEnterすると候補を絞れます。）',
            (l_in[:200])
        )
  
    submit_btn=st.form_submit_button('表示')
    cancel_btn=st.form_submit_button('消す')
    if submit_btn:
        if mul_sel:
            selected_query=mul_sel[0]
    #1個しか選択していないときmul_sel[1]を参照するとout of indexのエラーになるので対策
            try:
                selected_query1=mul_sel[1]
            except:
                selected_query1='windows アプリ 自動操作 python'
    #何も選択しないで表示を押したときの対策。適当なワードで表示する。
        else:
            selected_query='pandas 表計算'
            selected_query1='windows アプリ 自動操作 python'
        #グループ化により選ばれたクエリのみでデータフレーム作成
        df_a = df.groupby("上位のクエリ").get_group(selected_query)
        df_b = df.groupby("上位のクエリ").get_group(selected_query1)
        #列名'掲載順位'を各選ばれたクエリに変更
        df_a1=df_a.rename(columns={'掲載順位': selected_query})
        df_b1=df_b.rename(columns={'掲載順位': selected_query1})

        #日付のリスト化
        date_list = df['日付'].to_list()

        #重複削除-set()を使って重複削除すると、できたものがセット{}になって昔使えたlist()でリストにならないので、この方法はNG
        # date_list_set=set(date_list)

        #重複削除-これだとリストにできる
        date_list_set = []

        for i in date_list:
            if i not in date_list_set:
                date_list_set.append(i)
        #日付以外、空データのデータフレーム作成
        columns = ['上位のクエリ', '掲載順位','日付']
        df_x = pd.DataFrame(index=[], columns=columns)

        for i in date_list_set:
            list = [[None,None,i]]
            df_append = pd.DataFrame(data=list, columns=columns)
            df_x1 = pd.concat([df_x, df_append], ignore_index=True, axis=0)
            df_x=df_x1

        #データフレームと空のデータフレームを結合
        df_contact_a1=pd.concat([df_a1,df_x])
        df_contact_b1=pd.concat([df_b1,df_x])
        #日付が同じ行は削除、必ず空の行を後ろに結合する。前に入れると空の行がのこってしまう。
        df_a2=df_contact_a1.drop_duplicates(subset='日付')
        df_b2=df_contact_b1.drop_duplicates(subset='日付')
        #日付とクエリのデータフレーム作成
        df_a3=df_a2[['日付',selected_query]]
        df_b3=df_b2[['日付',selected_query1]]
        #日付の年市も2桁と月だけ切り出す
        df_a3['日付']=df_a3['日付'].str[2:7]
        df_b3['日付']=df_b3['日付'].str[2:7]
        #日付をキーにマージ
        df_contact=pd.merge(df_a3, df_b3, on='日付')
        #ソート
        df_a4 = df_a3.sort_values('日付')
        df_b4 = df_b3.sort_values('日付')
        #結果表の処理、グラフはa4、b4使う。欠損しているものを0または100にするとグラフがみにくくなるため。
        #欠損を0で埋める。Nanだと.round().astype(int)ができない。
        df_a5=df_a4.fillna(0)
        #検索順を四捨五入して少数から整数へ
        df_a5[selected_query]=df_a5[selected_query].round().astype(int)
        df_b5=df_b4.fillna(0)
        df_b5[selected_query1]=df_b5[selected_query1].round().astype(int)
        #結果を日付をキーにして結合
        result_df=pd.merge(df_a5,df_b5,on='日付')
        st.text('イチゲブログ検索ワード別検索順位　（0は検索順位圏外または、その月に検索されていない）')
        result_df
        #text内の改行は\n
        st.text('検索ワード”'+selected_query+'”または”'+selected_query1+'”を\nGoogleで検索してイチゲブログhttps://kikuichige.comが出るか確認してみてください。')
        #matplotlib
        fig,ax=plt.subplots()
        ax.invert_yaxis()
        #場複数系列の場合２つに分けか１つに２つ書く、この場合x軸同じでもx,y書く。この場合ラベルが使えない
        ax.plot(df_a4['日付'],df_a4[selected_query],label=selected_query,marker='o')
        ax.plot(df_b4['日付'],df_b4[selected_query1],label=selected_query1,marker='o')
        ax.set_title('イチゲブログ検索ワード別検索順位')
        ax.set_xlabel('日付')
        #y軸ラベル横書き
        ax.set_ylabel('検索順位',rotation='horizontal')
        ax.grid()
        #label表示に必要
        ax.legend()
        st.pyplot(fig)
        
        
