import streamlit as st
import pandas as pd
import plotly.express as px
from instaloader import Instaloader, Profile, InstaloaderException

# Ativar modo Wide
st.set_page_config(layout="wide", page_title="Comparação de Perfis do Instagram", page_icon="📊")

# Função para carregar dados do Instagram com cache
@st.cache_data(ttl=3600)
def get_instagram_data(username, max_posts=5):
    loader = Instaloader()
    
    
    profile = Profile.from_username(loader.context, username)
    data = {
        "Nome": profile.username,
        "Foto de Perfil": profile.profile_pic_url,
        "Seguidores": profile.followers,
        "Seguindo": profile.followees,
        "Postagens": profile.mediacount,
        "URL da Mídia": [],
        "Tipo de Mídia": [],
        "Curtidas": [],
        "Comentários": [],
        "Legenda": []
    }
    for i, post in enumerate(profile.get_posts()):
        if i >= max_posts:
            break
        data["URL da Mídia"].append(post.url)
        data["Tipo de Mídia"].append("Vídeo" if post.is_video else "Imagem")
        data["Curtidas"].append(post.likes)
        data["Comentários"].append(post.comments)
        data["Legenda"].append(post.caption)
    return data

# Função para criar gráficos de barras comparativos
def create_comparison_bar_chart(df, x, y, title, color, labels):
    fig = px.bar(df, x=x, y=y, color=color, barmode='group', labels=labels, title=title, text=y)
    fig.update_layout(showlegend=True)
    fig.update_traces(marker_line_width=0, textposition='outside')
    fig.update_layout(
        xaxis_title="Postagens",
        yaxis_title="Métricas",
        showlegend=True,
        legend_title="Perfil",
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=False),
    )
    return fig

# Título da aplicação
st.title("📈 Comparação de Perfis do Instagram")

# Função para calcular a taxa de engajamento
def calculate_engagement(likes, comments, followers):
    return (likes + comments) / followers * 100

# Sidebar para inputs
with st.sidebar:
    st.sidebar.image("logo.png", use_column_width=True)
    st.header("🔍 Detalhes da Análise")
    username_1 = st.text_input("Usuário do Instagram 1", placeholder="Digite o username...")
    username_2 = st.text_input("Usuário do Instagram 2", placeholder="Digite o username...")

    # Botão para análise
    analyze_button = st.button("🔍 Analisar")
    st.write("### 📝 Nossa tecnologia avançada analisa suas postagens e revela insights valiosos que podem transformar sua estratégia de conteúdo.")

# Verificar se o usuário já realizou uma análise
if "analysis_done" not in st.session_state:
    st.session_state.analysis_done = False

# Layout principal
if analyze_button and not st.session_state.analysis_done:
    if not all([username_1, username_2]):
        st.warning("⚠️ Por favor, preencha todos os campos de usuário.")
    else:
        try:
            profile_data_1 = get_instagram_data(username_1)
            profile_data_2 = get_instagram_data(username_2)
            st.session_state.analysis_done = True  # Atualizar o estado para indicar que a análise foi realizada
            st.success("✅ Análise realizada com sucesso!")
        except InstaloaderException as e:
            st.error(f"🚫 Erro ao obter dados dos perfis do Instagram: {e}")
else:
    if st.session_state.analysis_done:
        st.warning("⚠️ Você já realizou uma análise. Não é possível fazer outra na mesma sessão.")

# Se a análise foi realizada, continuar com o resto da lógica
if st.session_state.analysis_done:
    st.header("📊 Análise dos Dados")
    
    # Restante do código para exibir os resultados da análise...



    col1, col2 = st.columns(2)
    with col1:
        st.subheader(f"Perfil Analisado: {profile_data_1['Nome']}")
        #st.image(profile_data_1["Foto de Perfil"], caption=f"{profile_data_1['Nome']} - Foto de Perfil")
        st.write(f"**👥Seguidores:** {profile_data_1['Seguidores']}")
        st.write(f"**🔄Seguindo:** {profile_data_1['Seguindo']}")
        st.write(f"**📷Postagens:** {profile_data_1['Postagens']}")
        st.subheader("📲Última Postagem")
        if profile_data_1["Tipo de Mídia"][0] == "Vídeo":
            st.video(profile_data_1["URL da Mídia"][0])
        else:
            st.image(profile_data_1["URL da Mídia"][0], caption=profile_data_1["Legenda"][0])

    with col2:
        st.subheader(f"Perfil Analisado: {profile_data_2['Nome']}")
        #st.image(profile_data_2["Foto de Perfil"], caption=f"{profile_data_2['Nome']} - Foto de Perfil")
        st.write(f"**👥Seguidores:** {profile_data_2['Seguidores']}")
        st.write(f"**🔄Seguindo:** {profile_data_2['Seguindo']}")
        st.write(f"**📷Postagens:** {profile_data_2['Postagens']}")
        st.subheader("📲Última Postagem")
        if profile_data_2["Tipo de Mídia"][0] == "Vídeo":
            st.video(profile_data_2["URL da Mídia"][0])
        else:
            st.image(profile_data_2["URL da Mídia"][0], caption=profile_data_2["Legenda"][0])

    likes_df = pd.DataFrame({
        "Perfil": [profile_data_1["Nome"]]*len(profile_data_1["Curtidas"]) + [profile_data_2["Nome"]]*len(profile_data_2["Curtidas"]),
        "Postagem": [f"Post {i+1}" for i in range(len(profile_data_1["Curtidas"]))] + [f"Post {i+1}" for i in range(len(profile_data_2["Curtidas"]))],
        "Curtidas": profile_data_1["Curtidas"] + profile_data_2["Curtidas"]
    })

    comments_df = pd.DataFrame({
        "Perfil": [profile_data_1["Nome"]]*len(profile_data_1["Comentários"]) + [profile_data_2["Nome"]]*len(profile_data_2["Comentários"]),
        "Postagem": [f"Post {i+1}" for i in range(len(profile_data_1["Comentários"]))] + [f"Post {i+1}" for i in range(len(profile_data_2["Comentários"]))],
        "Comentários": profile_data_1["Comentários"] + profile_data_2["Comentários"]
    })

    engagement_df = pd.DataFrame({
        "Perfil": [profile_data_1["Nome"], profile_data_2["Nome"]],
        "Engajamento (%)": [
            calculate_engagement(sum(profile_data_1["Curtidas"]), sum(profile_data_1["Comentários"]), profile_data_1["Seguidores"]),
            calculate_engagement(sum(profile_data_2["Curtidas"]), sum(profile_data_2["Comentários"]), profile_data_2["Seguidores"])
        ]
    })

    #Dataframe para o gráfico de distribuição de tipos de mídia
    media_type_df = pd.DataFrame({
    "Perfil": [profile_data_1["Nome"]]*len(profile_data_1["Tipo de Mídia"]) + [profile_data_2["Nome"]]*len(profile_data_2["Tipo de Mídia"]),
    "Tipo de Mídia": profile_data_1["Tipo de Mídia"] + profile_data_2["Tipo de Mídia"]
    })

    # Dataframe para o gráfico de engajamento por tipo de mídia
    engagement_media_type_df = pd.DataFrame({
    "Perfil": [profile_data_1["Nome"]]*len(profile_data_1["Tipo de Mídia"]) + [profile_data_2["Nome"]]*len(profile_data_2["Tipo de Mídia"]),
    "Tipo de Mídia": profile_data_1["Tipo de Mídia"] + profile_data_2["Tipo de Mídia"],
    "Engajamento": [likes + comments for likes, comments in zip(profile_data_1["Curtidas"], profile_data_1["Comentários"])] +
                   [likes + comments for likes, comments in zip(profile_data_2["Curtidas"], profile_data_2["Comentários"])]
    })

    

    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(create_comparison_bar_chart(likes_df, x="Postagem", y="Curtidas", title="Curtidas por Postagem", color="Perfil", labels={"Curtidas": "Curtidas"}))
        st.caption("Comparação das curtidas recebidas em cada postagem de ambos os perfis.")

        # Gráfico de distribuição de tipos de mídia
        st.plotly_chart(
        px.histogram(media_type_df, x="Tipo de Mídia", color="Perfil", barmode="group", title="Distribuição de Tipos de Mídia (Imagem vs. Vídeo)", labels={"Tipo de Mídia": "Tipo de Mídia"}),
        use_container_width=True)
        st.caption("Proporção de imagens e vídeos postados por cada perfil.")

    with col2:
        st.plotly_chart(create_comparison_bar_chart(comments_df, x="Postagem", y="Comentários", title="Comentários por Postagem", color="Perfil", labels={"Comentários": "Comentários"}))
        st.caption("Comparação dos comentários recebidos em cada postagem de ambos os perfis.")

        # Gráfico de engajamento por tipo de mídia
        st.plotly_chart(
        px.box(engagement_media_type_df, x="Tipo de Mídia", y="Engajamento", color="Perfil", title="Engajamento por Tipo de Mídia", labels={"Engajamento": "Curtidas + Comentários"}),
        use_container_width=True
                            )
        st.caption("Comparação do engajamento (curtidas + comentários) entre imagens e vídeos para ambos os perfis.")

    avg_likes_1 = sum(profile_data_1["Curtidas"]) / len(profile_data_1["Curtidas"])
    avg_comments_1 = sum(profile_data_1["Comentários"]) / len(profile_data_1["Comentários"])
    avg_likes_2 = sum(profile_data_2["Curtidas"]) / len(profile_data_2["Curtidas"])
    avg_comments_2 = sum(profile_data_2["Comentários"]) / len(profile_data_2["Comentários"])




# Layout combinado para taxas de engajamento e média de curtidas/comentários
st.markdown(f"""
<div style="background-color: #f1f1f1; padding: 15px; border-radius: 8px; margin-bottom: 20px;">
    <p style="font-size: 16px;">
        A taxa de engajamento do perfil <strong>{profile_data_1['Nome']}</strong> é de <strong>{engagement_df['Engajamento (%)'][0]:.2f}%</strong>, 
        enquanto a taxa de engajamento do perfil <strong>{profile_data_2['Nome']}</strong> é de <strong>{engagement_df['Engajamento (%)'][1]:.2f}%</strong>.
    </p>
    <p style="font-size: 16px;">
        Em média, o perfil <strong>{profile_data_1['Nome']}</strong> recebe <strong>{avg_likes_1:.0f}</strong> curtidas e <strong>{avg_comments_1:.0f}</strong> comentários por postagem, 
        enquanto o perfil <strong>{profile_data_2['Nome']}</strong> recebe <strong>{avg_likes_2:.0f}</strong> curtidas e <strong>{avg_comments_2:.0f}</strong> comentários por postagem.
    </p>
</div>
""", unsafe_allow_html=True)


if avg_likes_1 > avg_likes_2:
    st.markdown(f"""
    <div style="background-color: #f1f1f1; padding: 15px; border-radius: 8px; margin-bottom: 10px;">
        O perfil <strong>{profile_data_1['Nome']}</strong> tem uma performance superior em termos de curtidas em comparação ao perfil 
        <strong>{profile_data_2['Nome']}</strong>. 👍
    </div>
    """, unsafe_allow_html=True)
else:
    st.markdown(f"""
    <div style="background-color: #f1f1f1; padding: 15px; border-radius: 8px; margin-bottom: 10px;">
        O perfil <strong>{profile_data_2['Nome']}</strong> tem uma performance superior em termos de curtidas em comparação ao perfil 
        <strong>{profile_data_1['Nome']}</strong>. 👍
    </div>
    """, unsafe_allow_html=True)

if avg_comments_1 > avg_comments_2:
    st.markdown(f"""
    <div style="background-color: #f1f1f1; padding: 15px; border-radius: 8px; margin-bottom: 10px;">
        Além disso, o perfil <strong>{profile_data_1['Nome']}</strong> também se destaca ao receber mais comentários em média por postagem. 💬
    </div>
    """, unsafe_allow_html=True)
else:
    st.markdown(f"""
    <div style="background-color: #f1f1f1; padding: 15px; border-radius: 8px; margin-bottom: 10px;">
        O perfil <strong>{profile_data_2['Nome']}</strong> se destaca ao receber mais comentários em média por postagem. 💬
    </div>
    """, unsafe_allow_html=True)

st.markdown("""
<div style="background-color: #f1f1f1; padding: 15px; border-radius: 8px; margin-bottom: 20px;">
    Essas informações indicam qual perfil está gerando mais interações em termos de curtidas e comentários, o que pode ser um indicativo de 
    maior relevância ou engajamento com o público.
</div>
""", unsafe_allow_html=True)

# Texto persuasivo próximo ao botão com melhoria no design
st.markdown("""
<div style='background-color: #f9f9f9; padding: 20px; border-radius: 10px; margin-top: 20px;'>
    <h2 style='text-align: center; color: #333;'>📚 Quer uma Análise Completa do Seu Perfil?</h2>
    <p style='text-align: center; font-size: 18px; color: #555;'>
        Obtenha um relatório detalhado com insights e estratégias personalizadas para o seu perfil por apenas 
        <strong style='color: #e63946;'>R$87,90</strong>. Este relatório inclui:
    </p>
    <ul style='font-size: 16px; color: #555; list-style-type: none; padding-left: 0;'>
        <li>✅ Análise detalhada das postagens com mais engajamento.</li>
        <li>✅ Horários de publicação ideais para o seu público.</li>
        <li>✅ Estratégias personalizadas para aumentar seguidores e engajamento.</li>
        <li>✅ Sugestões de conteúdo baseadas em tendências do seu nicho.</li>
    </ul>
</div>
""", unsafe_allow_html=True)

# Botão de solicitação com design aprimorado
if st.button("🚀 Garanta Sua Análise Agora!"):
    st.markdown("""
    <meta http-equiv="refresh" content="0; url= https://kf2mepwdf2r.typeform.com/to/UMMzA7qD">
    """, unsafe_allow_html=True)

# Estilo adicional para aprimorar o botão
st.markdown("""
<style>
.stButton > button {
    background-color: #e63946; /* Vermelho chamativo */
    color: white;
    border-radius: 10px;
    padding: 12px 24px;
    font-size: 18px;
    font-weight: bold;
    transition: background-color 0.3s ease;
}
.stButton > button:hover {
    background-color: #d62839; /* Vermelho mais escuro ao passar o mouse */
}
</style>
""", unsafe_allow_html=True)



