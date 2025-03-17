import streamlit as st
import sqlite3
import pandas as pd

# SQLite Database Setup
def get_connection():
    conn = sqlite3.connect('library.db')
    c = conn.cursor()
    # Create table if not exists
    c.execute('''CREATE TABLE IF NOT EXISTS books
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                 title TEXT NOT NULL,
                 author TEXT NOT NULL,
                 year INTEGER,
                 genre TEXT,
                 read_status BOOLEAN)''')
    conn.commit()
    return conn

# Streamlit UI
st.set_page_config(page_title="Personal Library Manager", layout="wide")

def main():
    st.title("📚 Personal Library Manager")
    
    menu = ["Add Book", "Remove Book", "Search Books", "View All Books", "Statistics"]
    choice = st.sidebar.selectbox("Menu", menu)

    if choice == "Add Book":
        st.header("Add New Book")
        with st.form("add_book_form"):
            title = st.text_input("Title*")
            author = st.text_input("Author*")
            year = st.number_input("Publication Year", min_value=1800, max_value=2100)
            genre = st.selectbox("Genre", ["Fiction", "Non-Fiction", "Science", "History", "Biography", "Other"])
            read_status = st.checkbox("Read Status")
            
            if st.form_submit_button("Add Book"):
                if title and author:
                    conn = get_connection()
                    c = conn.cursor()
                    c.execute('''INSERT INTO books 
                                (title, author, year, genre, read_status)
                                VALUES (?,?,?,?,?)''',
                            (title, author, year, genre, read_status))
                    conn.commit()
                    conn.close()
                    st.success("Book added successfully!")
                else:
                    st.warning("Please fill in all required fields (*)")

    elif choice == "Remove Book":
        st.header("Remove Book")
        book_id = st.number_input("Enter Book ID to Remove", min_value=1)
        if st.button("Remove"):
            conn = get_connection()
            c = conn.cursor()
            c.execute("DELETE FROM books WHERE id = ?", (book_id,))
            conn.commit()
            if c.rowcount > 0:
                st.success("Book removed successfully!")
            else:
                st.error("Book not found")
            conn.close()

    elif choice == "Search Books":
        st.header("Search Books")
        search_type = st.radio("Search By", ["Title", "Author"])
        search_query = st.text_input(f"Enter {search_type} to Search")
        
        if search_query:
            conn = get_connection()
            if search_type == "Title":
                query = "SELECT * FROM books WHERE title LIKE ?"
            else:
                query = "SELECT * FROM books WHERE author LIKE ?"
            
            c = conn.cursor()
            c.execute(query, (f'%{search_query}%',))
            results = c.fetchall()
            conn.close()
            
            if results:
                df = pd.DataFrame(results, columns=['ID', 'Title', 'Author', 'Year', 'Genre', 'Read Status'])
                st.dataframe(df.set_index('ID'))
            else:
                st.info("No matching books found")

    elif choice == "View All Books":
        st.header("Your Library Collection")
        conn = get_connection()
        c = conn.cursor()
        c.execute("SELECT * FROM books")
        all_books = c.fetchall()
        conn.close()
        
        if all_books:
            df = pd.DataFrame(all_books, columns=['ID', 'Title', 'Author', 'Year', 'Genre', 'Read Status'])
            st.dataframe(df.set_index('ID'))
        else:
            st.info("Your library is empty")

    elif choice == "Statistics":
        st.header("Library Statistics")
        conn = get_connection()
        c = conn.cursor()
        
        # Total books
        c.execute("SELECT COUNT(*) FROM books")
        total_books = c.fetchone()[0]
        
        # Read books
        c.execute("SELECT COUNT(*) FROM books WHERE read_status = 1")
        read_books = c.fetchone()[0]
        
        # Genre distribution
        c.execute("SELECT genre, COUNT(*) FROM books GROUP BY genre")
        genre_data = c.fetchall()
        
        conn.close()

        col1, col2 = st.columns(2)
        col1.metric("Total Books", total_books)
        if total_books > 0:
            col2.metric("Books Read", f"{read_books} ({read_books/total_books*100:.1f}%)")
        
        if genre_data:
            st.subheader("Genre Distribution")
            genre_df = pd.DataFrame(genre_data, columns=["Genre", "Count"])
            st.bar_chart(genre_df.set_index("Genre"))

if __name__ == "__main__":
    main()