from flask import Flask, request, jsonify
from flask_cors import CORS
from database import get_db_connection

app = Flask(__name__)
CORS(app)

@app.route('/api/books', methods=['GET'])
def get_books():
    try:
        book_id_param = request.args.get('book_id', '').strip()
        page = request.args.get('page', default=1, type=int)
        author = request.args.get('author', '').strip()
        topic = request.args.get('topic', '').strip()
        language = request.args.get('language', '').strip()
        mime_type = request.args.get('mime_type', '').strip()
        title = request.args.get('title', '').strip()
        
        if page < 1:
            page = 1
        
        limit = 25
        offset = (page - 1) * limit
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        joins = []
        where_conditions = []
        params = []
        
        if book_id_param:
            book_ids = []
            for x in book_id_param.split(','):
                x = x.strip()
                if x:
                    try:
                        book_ids.append(int(x))
                    except ValueError:
                        pass
            
            if book_ids:
                where_conditions.append("b.gutenberg_id = ANY(%s)")
                params.append(book_ids)
        
        if author:
            authors = []
            for x in author.split(','):
                x = x.strip()
                if x:
                    authors.append(f"%{x}%")
            
            if authors:
                joins.append("JOIN books_book_authors bba ON b.id = bba.book_id")
                joins.append("JOIN books_author a ON bba.author_id = a.id")
                author_conditions = []
                for author_search in authors:
                    author_conditions.append("a.name ILIKE %s")
                    params.append(author_search)
                where_conditions.append("(" + " OR ".join(author_conditions) + ")")
        
        if topic:
            topics = []
            for x in topic.split(','):
                x = x.strip()
                if x:
                    topics.append(f"%{x}%")
            
            if topics:
                joins.append("LEFT JOIN books_book_subjects bbs ON b.id = bbs.book_id")
                joins.append("LEFT JOIN books_subject s ON bbs.subject_id = s.id")
                joins.append("LEFT JOIN books_book_bookshelves bbb2 ON b.id = bbb2.book_id")
                joins.append("LEFT JOIN books_bookshelf bs ON bbb2.bookshelf_id = bs.id")
                topic_conditions = []
                for topic_search in topics:
                    topic_conditions.append("(s.name ILIKE %s OR bs.name ILIKE %s)")
                    params.append(topic_search)
                    params.append(topic_search)
                where_conditions.append("(" + " OR ".join(topic_conditions) + ")")
        
        if language:
            langs = []
            for x in language.split(','):
                x = x.strip()
                if x:
                    langs.append(x)
            
            if langs:
                joins.append("JOIN books_book_languages bbl ON b.id = bbl.book_id")
                joins.append("JOIN books_language l ON bbl.language_id = l.id")
                where_conditions.append("l.code = ANY(%s)")
                params.append(langs)
        
        if mime_type:
            mime_types = []
            for x in mime_type.split(','):
                x = x.strip()
                if x:
                    mime_types.append(x)
            
            if mime_types:
                joins.append("JOIN books_format f ON b.id = f.book_id")
                where_conditions.append("f.mime_type = ANY(%s)")
                params.append(mime_types)
        
        if title:
            title_search = f"%{title}%"
            where_conditions.append("b.title ILIKE %s")
            params.append(title_search)
        
        joins_str = " ".join(joins) if joins else ""
        where_clause = "WHERE " + " AND ".join(where_conditions) if where_conditions else ""
        
        books_query = f"""
            SELECT DISTINCT b.gutenberg_id as id, b.title, b.download_count
            FROM books_book b
            {joins_str}
            {where_clause}
            ORDER BY b.download_count DESC NULLS LAST
            LIMIT {limit} OFFSET {offset}
        """
        
        cursor.execute(books_query, params)
        books_data = cursor.fetchall()
        
        if not books_data:
            cursor.close()
            conn.close()
            return jsonify({'count': 0, 'results': []}), 200
        
        book_ids = [row[0] for row in books_data]
        book_titles = {row[0]: row[1] for row in books_data}
        
        authors_query = """
            SELECT b.gutenberg_id, a.id, a.name
            FROM books_book b
            JOIN books_book_authors bba ON b.id = bba.book_id
            JOIN books_author a ON bba.author_id = a.id
            WHERE b.gutenberg_id = ANY(%s)
        """
        cursor.execute(authors_query, (book_ids,))
        authors_data = {}
        for row in cursor.fetchall():
            book_id = row[0]
            author = {'id': row[1], 'name': row[2]}
            if book_id not in authors_data:
                authors_data[book_id] = []
            authors_data[book_id].append(author)
        
        languages_query = """
            SELECT b.gutenberg_id, l.code
            FROM books_book b
            JOIN books_book_languages bbl ON b.id = bbl.book_id
            JOIN books_language l ON bbl.language_id = l.id
            WHERE b.gutenberg_id = ANY(%s)
        """
        cursor.execute(languages_query, (book_ids,))
        languages_data = {}
        for row in cursor.fetchall():
            book_id = row[0]
            language = row[1]
            if book_id not in languages_data:
                languages_data[book_id] = []
            languages_data[book_id].append(language)
        
        subjects_query = """
            SELECT b.gutenberg_id, s.name
            FROM books_book b
            JOIN books_book_subjects bbs ON b.id = bbs.book_id
            JOIN books_subject s ON bbs.subject_id = s.id
            WHERE b.gutenberg_id = ANY(%s)
        """
        cursor.execute(subjects_query, (book_ids,))
        subjects_data = {}
        for row in cursor.fetchall():
            book_id = row[0]
            subject = row[1]
            if book_id not in subjects_data:
                subjects_data[book_id] = []
            subjects_data[book_id].append(subject)
        
        bookshelves_query = """
            SELECT b.gutenberg_id, bs.name
            FROM books_book b
            JOIN books_book_bookshelves bbb ON b.id = bbb.book_id
            JOIN books_bookshelf bs ON bbb.bookshelf_id = bs.id
            WHERE b.gutenberg_id = ANY(%s)
        """
        cursor.execute(bookshelves_query, (book_ids,))
        bookshelves_data = {}
        for row in cursor.fetchall():
            book_id = row[0]
            bookshelf = row[1]
            if book_id not in bookshelves_data:
                bookshelves_data[book_id] = []
            bookshelves_data[book_id].append(bookshelf)
        
        formats_query = """
            SELECT b.gutenberg_id, fmt.mime_type, fmt.url
            FROM books_book b
            JOIN books_format fmt ON b.id = fmt.book_id
            WHERE b.gutenberg_id = ANY(%s)
        """
        cursor.execute(formats_query, (book_ids,))
        formats_data = {}
        for row in cursor.fetchall():
            book_id = row[0]
            format_obj = {'mime_type': row[1], 'url': row[2]}
            if book_id not in formats_data:
                formats_data[book_id] = []
            formats_data[book_id].append(format_obj)
        count_query = f"SELECT COUNT(DISTINCT b.gutenberg_id) FROM books_book b {joins_str} {where_clause}"
        cursor.execute(count_query, params)
        total_count = cursor.fetchone()[0]
        
        cursor.close()
        conn.close()
        
        books = []
        for book_id in book_ids:
            languages = languages_data.get(book_id, [])
            books.append({
                'id': book_id,
                'title': book_titles.get(book_id, '') or '',
                'authors': authors_data.get(book_id, []),
                'language': languages[0] if languages else '',
                'subjects': subjects_data.get(book_id, []),
                'bookshelves': bookshelves_data.get(book_id, []),
                'download_links': formats_data.get(book_id, [])
            })
        
        return jsonify({'count': total_count, 'results': books}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
