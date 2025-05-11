import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
import datetime

# --- Configuration and Constants ---
SHEET_NAME_PAST_MEETUPS = "Past_Meetups"
SHEET_NAME_NEXT_MEETUP = "Next_Meetup"
SHEET_NAME_PRESENTER_INTEREST = "Presenter_Interest"
STOP_WORDS = {
    'a', 'an', 'the', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
    'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'should',
    'can', 'could', 'may', 'might', 'must', 'about', 'above', 'after',
    'again', 'against', 'all', 'am', 'and', 'any', 'as', 'at', 'because',
    'before', 'below', 'between', 'both', 'but', 'by', 'com', 'for',
    'from', 'further', 'here', 'how', 'i', 'if', 'in', 'into', 'it', 'its',
    'itself', 'just', 'k', 'me', 'more', 'most', 'my', 'myself', 'no', 'nor',
    'not', 'now', 'o', 'of', 'off', 'on', 'once', 'only', 'or', 'other',
    'our', 'ours', 'ourselves', 'out', 'over', 'own', 'r', 's', 'same',
    'she', "shes", 'so', 'some', 'such', 't', 'than', 'that', "thatll",
    'their', 'theirs', 'them', 'themselves', 'then', 'there', 'these',
    'they', 'this', 'those', 'through', 'to', 'too', 'under', 'until',
    'up', 'very', 'what', 'when', 'where', 'which', 'while', 'who', 'whom',
    'why', 'with', 'you', "youd", "youll", "youre", "youve", 'your',
    'yours', 'yourself', 'yourselves', 'meetup', 'meetups', 'topic', 'topics',
    'presentation', 'presentations', 'information', 'info', 'on', 'covered',
    'past', 'next', 'upcoming', 'want', 'present', 'talk', 'speak'
}

# --- Google Sheets Connection (assuming functions connect_gsheets, get_sheet_data_as_df, get_next_meetup_info, log_presenter_interest, clean_query exist as before) ---
def connect_gsheets():
    """Connects to Google Sheets using credentials from Streamlit secrets."""
    try:
        creds_dict = st.secrets["google_service_account"]
        creds = Credentials.from_service_account_info(
            creds_dict,
            scopes=[
                "https://www.googleapis.com/auth/spreadsheets",
                "https://www.googleapis.com/auth/drive.readonly"
            ],
        )
        gc = gspread.authorize(creds)
        return gc
    except Exception as e:
        st.error(f"Error connecting to Google Sheets: {e}")
        st.error("Please ensure your `secrets.toml` is configured correctly with Google Service Account credentials.")
        return None

gc = connect_gsheets()

def get_sheet_data_as_df(gc_conn, sheet_name):
    if not gc_conn: return pd.DataFrame()
    try:
        spreadsheet = gc_conn.open_by_key(st.secrets["google_sheet_id"])
        worksheet = spreadsheet.worksheet(sheet_name)
        data = worksheet.get_all_records()
        return pd.DataFrame(data)
    except gspread.exceptions.WorksheetNotFound:
        st.warning(f"Sheet '{sheet_name}' not found.")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Error fetching data from sheet '{sheet_name}': {e}")
        return pd.DataFrame()

def get_next_meetup_info(gc_conn):
    if not gc_conn: return None
    try:
        spreadsheet = gc_conn.open_by_key(st.secrets["google_sheet_id"])
        worksheet = spreadsheet.worksheet(SHEET_NAME_NEXT_MEETUP)
        data = worksheet.get_all_records()
        return data
    except gspread.exceptions.WorksheetNotFound:
        st.warning(f"Sheet '{SHEET_NAME_NEXT_MEETUP}' not found.")
        return None
    except Exception as e:
        st.error(f"Error fetching next meetup info: {e}")
        return None

def log_presenter_interest(gc_conn, name, email):
    if not gc_conn: return False
    try:
        spreadsheet = gc_conn.open_by_key(st.secrets["google_sheet_id"])
        worksheet = spreadsheet.worksheet(SHEET_NAME_PRESENTER_INTEREST)
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        worksheet.append_row([timestamp, name, email])
        return True
    except gspread.exceptions.WorksheetNotFound:
        st.error(f"Sheet '{SHEET_NAME_PRESENTER_INTEREST}' not found. Could not log interest.")
        return False
    except Exception as e:
        st.error(f"Error logging presenter interest: {e}")
        return False

def clean_query(query_text):
    if not query_text or not isinstance(query_text, str): return []
    words = query_text.lower().split()
    cleaned_words = [word for word in words if word not in STOP_WORDS]
    return cleaned_words

# --- Streamlit App UI ---
st.set_page_config(page_title="CNJ Data Science Meetup Bot", layout="wide")
st.title("🤖 Central NJ Data Science Meetup Knowledge Agent")

if 'user_name' not in st.session_state: st.session_state.user_name = ""
if 'user_email' not in st.session_state: st.session_state.user_email = ""
if 'authenticated' not in st.session_state: st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.header("👋 Hi, what is your name?")
    name_input = st.text_input("Your Name:", key="name_input_field")
    email_input = st.text_input("Your Email Address:", key="email_input_field")
    if st.button("Submit", key="auth_button"):
        if name_input and email_input:
            if "@" in email_input and "." in email_input:
                st.session_state.user_name = name_input
                st.session_state.user_email = email_input
                st.session_state.authenticated = True
                st.rerun()
            else: st.error("Please enter a valid email address.")
        else: st.warning("Please enter both your name and email address.")
else:
    st.sidebar.header(f"Hello {st.session_state.user_name}!")
    st.sidebar.write("Welcome to the Central NJ Data Science Meetup!")
    menu_options = {
        "ℹ️ Info on Past Meetups": 1,
        "📅 Info on Next Meetup": 2,
        "🎤 Present in Upcoming Meetup": 3
    }
    choice_str = st.sidebar.radio("What would you like to do?", options=list(menu_options.keys()), key="menu_choice")
    user_choice = menu_options[choice_str]




    if gc:
        if user_choice == 1:
            st.subheader("📚 Search Past Meetups")
            search_query = st.text_input("Enter keywords to search by topic, title, or presenter:", key="search_query_past")
            if search_query:
                past_meetups_df = get_sheet_data_as_df(gc, SHEET_NAME_PAST_MEETUPS)
                if not past_meetups_df.empty:
                    cleaned_keywords = clean_query(search_query)
                    if not cleaned_keywords:
                        st.info("Please try more specific keywords.")
                    else:
                        results_df = past_meetups_df[
                            past_meetups_df.apply(
                                lambda row: any(
                                    keyword in str(row.get('Presentation Title', '')).lower() or
                                    keyword in str(row.get('Synopsis', '')).lower() or
                                    keyword in str(row.get('Presenter', '')).lower()
                                    for keyword in cleaned_keywords
                                ),
                                axis=1
                            )
                        ]
                        if not results_df.empty:
                            st.write(f"Found {len(results_df)} results:")
                            for index, row in results_df.iterrows():
                                st.markdown(f"---")
                                if 'Presentation Title' in row and row['Presentation Title'] and 'PDF_Link' in row and row['PDF_Link']:
                                    st.markdown(f"**Presentation Title:** [{row['Presentation Title']}]({row['PDF_Link']})")
                                elif 'Presentation Title' in row and row['Presentation Title']:
                                    st.markdown(f"**Presentation Title:** {row['Presentation Title']}")
                                if 'Synopsis' in row and row['Synopsis']: st.markdown(f"**Synopsis:** {row['Synopsis']}")
                                    #with st.expander("Synopsis"): st.write(row['Synopsis'])
                                if 'Presenter' in row and row['Presenter']: st.markdown(f"**Presenter:** {row['Presenter']}")
                                if 'Month/Year' in row and row['Month/Year']: st.markdown(f"**Month/Year:** {row['Month/Year']}")
                            st.markdown(f"---")
                        else: st.info(f"No past meetups found matching your query: '{search_query}'. Try different keywords.")
                else: st.warning("Could not retrieve past meetup data. The sheet might be empty or inaccessible.")
            else: st.info("Type some keywords above to search for past meetups.")

        elif user_choice == 2:
            st.subheader("🗓️ Next Meetup Information")
            next_meetup_data = get_next_meetup_info(gc)
            if next_meetup_data:
                if isinstance(next_meetup_data, list) and len(next_meetup_data) > 0:
                    for i, meetup in enumerate(next_meetup_data):
                        if i > 0: st.markdown("---")
                        st.markdown(f"**Presentation Title:** {meetup.get('Presentation Title', 'N/A')}")
                        #synopsis = meetup.get('Synopsis', 'Not available.')                        
                        #with st.expander("Synopsis"): st.write(synopsis if synopsis else "Not available.")
                        st.markdown(f"**Synopsis:** {meetup.get('Synopsis', 'Not available.')}")
                        st.markdown(f"**Presenter:** {meetup.get('Presenter', 'N/A')}")
                else: st.info("Information for the next meetup is not yet available. Please check back later.")
            else: st.info("Information for the next meetup is not yet available or could not be retrieved. Please check back later.")

        # --- MODIFIED: 3. Present in upcoming meetup ---
        elif user_choice == 3:
            st.subheader("💡 Present in an Upcoming Meetup")

            # Initialize option3_status if it doesn't exist at all
            if 'option3_status' not in st.session_state:
                st.session_state.option3_status = 'ask_confirmation'
                
            current_status = st.session_state.option3_status # Will be 'ask_confirmation' due to logic above

            if current_status == 'ask_confirmation':
                st.write(f"You have indicated that you'd like to present at an upcoming meetup.")
                st.write(f"If you confirm, we will note your interest and share your name ({st.session_state.user_name}) and email ({st.session_state.user_email}) with the organizers for follow-up.")
                st.warning("Do you want to proceed and confirm your interest?")

                col_confirm, col_cancel = st.columns(2)
                with col_confirm:
                    if st.button("✅ Yes, Confirm My Interest", key="present_yes", use_container_width=True):
                        if log_presenter_interest(gc, st.session_state.user_name, st.session_state.user_email):
                            st.session_state.option3_status = 'logged'
                        else:
                            st.session_state.option3_status = 'logging_failed'
                        st.rerun() # Rerun to show the result of the action
                with col_cancel:
                    if st.button("❌ No, Cancel", key="present_no", use_container_width=True):
                        st.session_state.option3_status = 'cancelled'
                        st.rerun() # Rerun to show the cancellation message

            elif current_status == 'logged':
                st.success(f"Thank you, {st.session_state.user_name}! Your interest in presenting has been recorded. We will contact you at {st.session_state.user_email} for further details.")
                st.balloons()
                # User stays in this view until they select another option from the sidebar.
                # The logic at the top will reset option3_status to 'ask_confirmation' if they re-select option 3.

            elif current_status == 'logging_failed':
                st.error("There was an issue recording your interest. Please try again later or contact the organizers directly.")
                # User stays in this view. Re-selecting option 3 will reset to 'ask_confirmation'.

            elif current_status == 'cancelled':
                st.info("Okay, your interest has not been recorded. You can select another option from the sidebar.")
                st.session_state.option3_status = 'ask_confirmation'

    else:
        st.error("The Knowledge Agent is currently unable to connect to its data source. Please try again later.")

    if st.sidebar.button("Log out", key="logout_button"):
        st.session_state.authenticated = False
        st.session_state.user_name = ""
        st.session_state.user_email = ""
        # Clear specific states on logout
        if 'option3_status' in st.session_state:
            del st.session_state.option3_status
        st.rerun()

st.markdown("---")
st.caption("Central NJ Data Science Meetup Bot")