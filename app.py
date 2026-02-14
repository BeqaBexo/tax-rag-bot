"""
Streamlit Web აპლიკაცია
"""
import sys
from pathlib import Path

project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))
sys.path.insert(0, str(project_root / "src" / "services"))
sys.path.insert(0, str(project_root / "config"))

import streamlit as st
from src.services.rag_service import RAGService
from config.settings import settings

# Direct import without ui module
import yaml

# Load UI configurations directly
def load_css():
    css_path = settings.CONFIG_DIR / "ui" / "styles.css"
    try:
        with open(css_path, 'r', encoding='utf-8') as f:
            return f.read()
    except:
        return ""

def load_ui_config():
    config_path = settings.CONFIG_DIR / "ui" / "ui_config.yaml"
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    except:
        return {}

def load_sample_questions():
    questions_path = settings.CONFIG_DIR / "ui" / "sample_questions.yaml"
    try:
        with open(questions_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
            return data.get('all_questions', [])
    except:
        return [
            "რა არის დღგ?",
            "როგორ უნდა გადავიხადო საშემოსავლო გადასახადი?",
            "რა დოკუმენტები მჭირდება ბიზნესის რეგისტრაციისთვის?",
        ]

# Load configurations
css = load_css()
config = load_ui_config()
sample_questions = load_sample_questions()

# Page config
st.set_page_config(
    page_title=config.get('page', {}).get('title', settings.UI_TITLE),
    page_icon=config.get('page', {}).get('icon', settings.UI_ICON),
    layout=config.get('page', {}).get('layout', 'wide'),
    initial_sidebar_state=config.get('page', {}).get('initial_sidebar_state', 'expanded')
)

# Apply CSS
if css:
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)

# Session state
if 'rag_service' not in st.session_state:
    st.session_state.rag_service = None
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'initialized' not in st.session_state:
    st.session_state.initialized = False


def initialize_rag_service():
    """RAG სერვისის ინიციალიზაცია"""
    if st.session_state.rag_service is None:
        try:
            with st.spinner('⏳ ვტვირთავ RAG სისტემას...'):
                # Check if Vector DB exists, if not - create it
                from src.services.vectordb_service import VectorDBService
                import os
                
                vectordb_service = VectorDBService()
                
                # If Vector DB doesn't exist, create it
                if not os.path.exists(settings.VECTOR_DB_DIR) or len(os.listdir(settings.VECTOR_DB_DIR)) == 0:
                    st.info('📊 პირველი გაშვება - ვქმნი Vector Database-ს...')
                    st.info('⏳ ეს შეიძლება 2-3 წუთი გასტანოს...')
                    
                    # Create Vector DB from documents
                    vectordb_service.create_database(force_recreate=True)
                    
                    st.success('✅ Vector Database შეიქმნა!')
                
                # Now initialize RAG service
                st.session_state.rag_service = RAGService(prompt_type="base")
                st.session_state.initialized = True
            
            st.success('✅ სისტემა მზადაა!')
            return True
        except Exception as e:
            st.error(f'❌ შეცდომა: {e}')
            import traceback
            st.error(traceback.format_exc())
            return False
    return True


# Header
header_config = config.get('header', {})
st.markdown(f"""
<h1 class="main-header">{settings.UI_ICON} {header_config.get('main_title', settings.UI_TITLE)}</h1>
<div class="sub-header">{header_config.get('subtitle', 'დამიხმარე საგადასახადო კითხვებში')}</div>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    sidebar_config = config.get('sidebar', {}).get('sections', [])
    
    if sidebar_config:
        for section in sidebar_config:
            if section['name'] == 'info':
                st.header(section['title'])
                if st.session_state.initialized and section.get('show_stats'):
                    stats = st.session_state.rag_service.get_stats()
                    st.metric("დოკუმენტები", stats['documents_in_db'])
                    st.metric("კითხვები", len(st.session_state.chat_history))
            
            elif section['name'] in ['how_it_works', 'sources']:
                st.header(section['title'])
                st.markdown(section.get('content', ''))
    else:
        # Default sidebar if no config
        st.header("ℹ️ ინფორმაცია")
        if st.session_state.initialized:
            stats = st.session_state.rag_service.get_stats()
            st.metric("დოკუმენტები", stats['documents_in_db'])
            st.metric("კითხვები", len(st.session_state.chat_history))
    
    st.markdown("---")
    st.header("⚙️ მოქმედებები")
    
    if st.button("🔄 გადატვირთვა"):
        st.session_state.rag_service = None
        st.session_state.initialized = False
        st.rerun()
    
    if st.button("🗑️ გაწმენდა"):
        st.session_state.chat_history = []
        st.rerun()

# Initialize
if not st.session_state.initialized:
    initialize_rag_service()

# Main Interface
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("💬 დასვი კითხვა")
    
    input_config = config.get('input', {})
    
    question = st.text_input(
        "კითხვა:",
        placeholder=input_config.get('placeholder', 'მაგ: რა არის დღგ?'),
        label_visibility="collapsed"
    )
    
    if input_config.get('show_sample_questions', True):
        st.write(f"**{input_config.get('sample_questions_label', 'ან აირჩიე მზა კითხვა:')}**")
        selected = st.selectbox(
            "მზა კითხვები:",
            [input_config.get('sample_questions_default', 'აირჩიე კითხვა...')] + sample_questions,
            label_visibility="collapsed"
        )
    
    search_clicked = st.button(
        input_config.get('search_button_text', '🔍 ძებნა'),
        type="primary",
        use_container_width=True
    )

with col2:
    tips_config = config.get('tips', {})
    st.subheader(tips_config.get('title', '🎯 რჩევები'))
    
    st.markdown("""
    **კარგი კითხვისთვის:**
    - იყავი კონკრეტული
    - გამოიყენე ქართული ენა
    - დასვი ერთი კითხვა
    
    **მაგალითები:**
    - ✅ "რა არის დღგ-ის განაკვეთი?"
    - ✅ "როგორ დავარეგისტრირო ბიზნესი?"
    - ❌ "მიამბე ყველაფერი"
    """)

# Process question
final_question = None
if search_clicked:
    if question.strip():
        final_question = question
    elif selected and selected != input_config.get('sample_questions_default', 'აირჩიე კითხვა...'):
        final_question = selected

if final_question and st.session_state.initialized:
    with st.spinner('🔎 ვეძებ პასუხს...'):
        try:
            response = st.session_state.rag_service.ask(final_question)
            st.session_state.chat_history.insert(0, response)
        except Exception as e:
            st.error(f'❌ შეცდომა: {e}')

# Chat History
if st.session_state.chat_history:
    st.markdown("---")
    st.header("📜 ისტორია")
    
    for chat in st.session_state.chat_history:
        st.markdown(f'<div class="question-box"><strong>❓ შენ:</strong><br>{chat["question"]}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="answer-box"><strong>🤖 ასისტენტი:</strong><br>{chat["answer"]}</div>', unsafe_allow_html=True)
        
        with st.expander("📚 წყაროები"):
            for i, src in enumerate(chat['sources'], 1):
                st.markdown(f'<div class="source-box"><strong>{i}. {src["file"]}</strong><br>📄 გვერდი: {src["page"]}<br><em>{src["content_preview"]}</em></div>', unsafe_allow_html=True)
        
        st.markdown("---")

# Footer
footer_config = config.get('footer', {})
footer_text = footer_config.get('text', '🔒 ინფორმაცია დაცულია | Version {version}')
st.markdown(f"""
<div style='text-align: center; color: #999; padding: 1rem;'>
    <small>{footer_text.format(version=settings.VERSION, environment=settings.ENVIRONMENT)}</small>
</div>
""", unsafe_allow_html=True)