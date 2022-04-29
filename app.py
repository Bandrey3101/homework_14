from flask import Flask, jsonify
import sqlite3


def main():
    app = Flask(__name__)
    app.config['JSON_AS_ASCII'] = False

    def connect_db(query):
        with sqlite3.connect('netflix.db') as connection:
            cursor = connection.cursor()
            cursor.execute(query)
            result = cursor.fetchall()
            return result


    @app.route('/movie/<title>')
    def search_title(title):
        query = f'''
            SELECT title, country, release_year, listed_in, description
            FROM netflix
            WHERE title = '{title}'
            ORDER BY release_year DESC
            LIMIT 1
        '''
        if not connect_db(query):
            return ('Такого фильма нет')
        else:
            response = connect_db(query)[0]
            response_json = {
                'title': response[0],
                'country': response[1],
                'release_year': response[2],
                'listed_in': response[3],
                'description': response[4]
            }

        return jsonify(response_json)


    @app.route('/movie/<int:start>/to/<int:end>')
    def search_period(start, end):
        query = f'''
               SELECT title, release_year
               FROM netflix
               WHERE release_year BETWEEN {start} AND {end}
               ORDER BY release_year
               LIMIT 100
        '''
        response = connect_db(query)
        response_json = []
        for film in response:
            response_json.append({
                'title': film[0],
                'release_year': film[1],
            })
        return jsonify(response_json)


    @app.route('/rating/<group>')
    def search_rating(group):
        levels = {
            'children': ['G'],
            'family': ['G', 'PG', 'PG-13'],
            'adult': ['R', 'NC-17']
        }
        if group in levels:
            level = '\", \"'.join(levels[group])
            level = f'\"{level}\"'
        else:
            return jsonify([])

        query = f'''
                   SELECT title, rating, description
                   FROM netflix
                   WHERE rating IN ({level})
                   ORDER BY release_year
                   LIMIT 100
        '''
        response = connect_db(query)
        response_json = []
        for film in response:
            response_json.append({
                'title': film[0],
                'rating': film[1],
                'description': film[2]
            })
        return jsonify(response_json)

    @app.route('/ganre/<ganre>')
    def search_ganre(ganre):
        query = f'''
            SELECT title, description, release_year
            FROM netflix
            WHERE listed_in = '{ganre}'
            ORDER BY release_year DESC
            LIMIT 10
        '''
        response = connect_db(query)
        response_json = []
        for film in response:
            response_json.append({
                'title': film[0],
                'description': film[1]
            })
        return jsonify(response_json)

    app.run(debug=True)

    def get_actors(name1='Rose McIver', name2='Ben Lamb'):
        query = f"""
            SELECT "cast"
            FROM netflix
            WHERE "cast" LIKE '%{name1}%' AND "cast" LIKE '%{name2}%'
        """
        response = connect_db(query)
        actors = []
        for cast in response:
            actors.extend(cast[0].split(', '))
        result = []
        for a in actors:
            if a not in [name1, name2]:
                if actors.count(a) > 2:
                    result.append(a)
        result = set(result)
        print(result)

    get_actors()


    def get_films(type_film, release_year, ganre):
        query = f"""
            SELECT title, description
            FROM netflix
            WHERE "type" = '{type_film}' AND release_year = {release_year} AND listed_in LIKE '%{ganre}%'
        """
        response = connect_db(query)
        response_json = []
        for film in response:
            response_json.append({
                'title': film[0],
                'description': film[1],
                'type': film[2]
            })
        return jsonify(response_json)
    print(get_films(type_film='Movie', release_year=2016, ganre='Drama'))





if __name__ == '__main__':
    main()
