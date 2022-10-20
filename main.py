import sqlite3
import flask
import prettytable
from flask import json

# Press the green button in the gutter to run the script.

#можно вместо использования параметров в Reponse сделать так:
#app.config['JSON_AS_ASCII']= False


def run_sql(sql):
    with sqlite3.connect("netflix.db") as connection:
        connection.row_factory = sqlite3.Row
        result = []
        for item in connection.execute(sql).fetchall():
            result.append(dict(item))
        return result

app = flask.Flask(__name__)

@app.route('/movie/<title>', methods = ['GET', 'POST'])

#Step 1
def get_movies_by_title(title):
    sql = f'''select title, country, release_year, listed_in as genre, description
          from netflix 
          where title = "{title}" 
          order by date_added desc 
          limit 1 '''
    result = run_sql(sql)
    if result:
        result = result[0]

    return flask.jsonify(result)
    #в виде словаря не подходит, надо в формате json
    #можно возвращать через response
    #return app.response_class(json.dumps(result, ensure_asci = False, ident = 4), minetype = 'application/json')

@app.get('/movie/<int:start_year>/to/<int:end_year>')

#task_2
def get_movie_by_period(start_year, end_year):
    sql = f'''select title, release_year
              from netflix 
              where release_year between {start_year} and {end_year}
              limit 100 '''
    return flask.jsonify(run_sql(sql))


#Step_3
@app.get('/rating/<rating>')
def get_by_rating(rating):
    my_dict = {
        "children":("G", "G"),
        "family": ("G", "PG", "PG-13"),
        "adult": ("R", "NC-17")
    }

    sql = f'''select title, rating, description
                  from netflix 
                  where rating in {my_dict.get(rating, ('PG-13', 'NC-17'))}
--                   лучше использовать get чем обращение через [], так как при отсутствующих ключах возвратит None
                   '''
    return flask.jsonify(run_sql(sql))

#Step_4
@app.get('/genre/<genre>')
def get_by_genre(genre):
    sql = f'''select title, rating, description
                      from netflix 
                      where listed_in like '%{genre.title()}%' 
                      order by release_year desc
                      limit 10
           '''
    return flask.jsonify(run_sql(sql))

#Step 5
def get_by_cast(actor_1 = 'Rose McIver', actor_2 = 'Ben Lamb'):
    sql = f'''select "cast"
                  from netflix 
                  where "cast" like '%{actor_1}%' and "cast" like '%{actor_2}%'
               '''
    result = run_sql(sql)
    # print(result)

    names_encountered = {}
    for item in result:
        names = item.get('cast').split(", ")
        for name in names:
            if name not in [actor_1, actor_2]:
                # if name in names_encountered.keys():
                #     names_encountered[name] += 1
                # else:
                #     names_encountered[name] = 1
                names_encountered[name] = names_encountered.get(name, 0) + 1
                #можно еще сдалеть через setdefault
                #также вместо проверки на вхождение двух заданных имен можно их удалить из словаря
                #names_encountered.__delete__(name)
    result = []
    for item in names_encountered:
        if names_encountered[item] > 2:
            result.append(item)

    return result

def get_by_type_and_year(types = 'TV Show', release_year = 2021, genre = 'TV'):
    sql = f'''select *
          from netflix 
          where type  = '{types}'
          and release_year = '{release_year}'
          and listed_in like '%{genre}%' 
                   '''
    return flask.jsonify(run_sql(sql))
    # return json.dumps(run_sql(sql), indent = 4, ensure_ascii = False)


if __name__ == '__main__':
    app.run(debug = True)

    #при debug = True идет постоянная перезагрузка main

#тестировать можно через curl - на windows его нет, надо устанавливать (гугл - установить curl), mcOs, Linux - пол умолчанию
#curl -v localhost:5000/movie/Hilda

# sql = ("""            SELECT title, release_year
#                         from netflix
#                         where type = 'Movie'
#                         and release_year between 1943 and 1945
#                         """)  # TODO измените код запроса
# эта конструкция вернет список объектов'
# а дальше - мы получим список словарей - каждая запись (строка - словарь)
#for item in run_sql(sql):
 #   print(dict(item))
""