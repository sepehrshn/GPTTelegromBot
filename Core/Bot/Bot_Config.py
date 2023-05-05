import telebot
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup, InlineQueryResultArticle, InputTextMessageContent, ForceReply
import Core.IMDB.IMDB_API_URL as imdb
import Core.GPT.GPT as gpt

telegramToken = '6265426880:AAFHClwUcG43xlINHXkmpDpXrTFqWWjg7SI'

bot = telebot.TeleBot(telegramToken)
username = bot.get_me().username
print(username)

@bot.message_handler(commands=['start'])
def Wellcome_Message(message):
    keyboard = InlineKeyboardMarkup(row_width=3)
    search_button = InlineKeyboardButton(text="Search Movie", switch_inline_query_current_chat='')
    genres_button = InlineKeyboardButton(text="Movie's Gnres", callback_data="/genres")
    gpt_button = InlineKeyboardButton(text="Chat GPT", callback_data="/gptsuggest")
    about_button = InlineKeyboardButton(text="About Bot", callback_data="/about")
    keyboard.add(search_button, genres_button, gpt_button, about_button)
    bot.send_message(message.chat.id, """
    Welcome To my Bot🎬
In this bot You can Search your movie's Name And See Details📽️
Search Movie By Genres🔦
Use Chat GPT to explain Your Movie Theme and See Suggestion🪩
Stay with US🐉
    """, reply_markup=keyboard)


@bot.message_handler(commands=['help'])
def Help(message):
    keyboard = InlineKeyboardMarkup(row_width=3)
    search_button = InlineKeyboardButton(text="Search Movie", switch_inline_query_current_chat='')
    genres_button = InlineKeyboardButton(text="Movie's Genres", callback_data="/genres")
    gpt_button = InlineKeyboardButton(text="Chat GPT", callback_data="/gptsuggest")
    keyboard.add(search_button, genres_button, gpt_button)
    bot.send_message(message.chat.id, "Choose one of These:", reply_markup=keyboard)
    


@bot.message_handler(commands=['gptsuggest'])
def GPT_Search(message):
    chat_id = message.chat.id
    replay_message = bot.send_message(chat_id, 'Enter the theme of the movie you like as in the example(space, time travel, animation, ...):')
    bot.register_next_step_handler(replay_message, GPT_Suggest_Result)


@bot.message_handler(commands=['about'])
def About(message):
    chat_id = message.chat.id
    replay_message = bot.send_message(chat_id, 'The pyTelegrambotapi(telebot), openai, Flask libraries  has been used to implement this robot')
    bot.register_next_step_handler(replay_message, GPT_Suggest_Result)


@bot.message_handler(commands=['search'])
def Search(message):
    chat_id = message.chat.id
    button = InlineKeyboardButton(text='Search Movie', switch_inline_query_current_chat='')
    keboard = InlineKeyboardMarkup().add(button)
    replay_message = bot.send_message(chat_id, 'Enter Your Movie\'s Name:', reply_markup=keboard)
    bot.register_next_step_handler(replay_message, Movie_with_Search)


@bot.message_handler(commands=['genres'])
def Genres(message):
    keyboard = InlineKeyboardMarkup(row_width=3)
    action = InlineKeyboardButton(text="Action", callback_data="genres_action")
    drama = InlineKeyboardButton(text="Drama", callback_data="genres_drama")
    family = InlineKeyboardButton(text="Family", callback_data="genres_family")
    fun = InlineKeyboardButton(text="Fun", callback_data="genres_fun")
    animation = InlineKeyboardButton(text="Animation", callback_data="genres_animation")
    scifi = InlineKeyboardButton(text="Sci-fi", callback_data="genres_scifi")
    horror = InlineKeyboardButton(text="Horror", callback_data="genres_horror")
    inLove = InlineKeyboardButton(text="In Love", callback_data="genres_inlove")
    keyboard.add(action, drama, family, fun, animation, scifi, horror, inLove)
    bot.send_message(message.chat.id, """Choose Your Favourite Genre:""", reply_markup=keyboard)


@bot.inline_handler(lambda query: len(query.query) > 0)
def Movie_with_Search(query):
    results = []
    text = query.query
    if len(text)>3 :
        movies = imdb.SearchByTitle(text)
        if movies is not None:
            for item in movies:
                article = InlineQueryResultArticle(
                    id=item['id'],
                    title=item['title'],
                    description=item['description'],
                    input_message_content= InputTextMessageContent(message_text = "movie_{0}".format(item['id'])),
                    thumbnail_url=item['image'],
                )
                results.append(article)
            bot.answer_inline_query(query.id, results)
        else:
            article = InlineQueryResultArticle(title='No Movie')
            bot.answer_inline_query(query.id, article)


def GPT_Suggest_Result(message):
    text = message.text
    movies = gpt.Suggestion(text)
    keyboard = InlineKeyboardMarkup()
    for item in movies:
        button = InlineKeyboardButton(text=item, callback_data="gpt_{0}".format(item))
        keyboard.add(button)
    bot.send_message(message.chat.id, 'Suggestion Movies:' ,reply_markup=keyboard)


def Create_Movie_Result(id, movies):
    if len(movies) == 0:
        bot.register_next_step_handler("No Movies!!!", Search_Error_Handler)
    else:
        for item in movies:
            keyboard = InlineKeyboardMarkup()
            title = item['title']
            _id = item['id']
            description = item['description']
            if 'None' not in item['image']:
                thumb_url = item['image']
            button = InlineKeyboardButton(text=title, callback_data="movie_{0}".format(_id))
            keyboard.add(button)
            bot.send_photo(id, thumb_url,caption=title, reply_markup=keyboard)
        

@bot.callback_query_handler(func=lambda call: call.data.startswith('genres_'))
def Movie_in_Genres(call):
    chat_id = call.from_user.id
    movies=[]
    if call.data == 'genres_action':
        movies = imdb.SearchByGenres('action')
    elif call.data == 'genres_drama':
        movies = imdb.SearchByGenres('drama')
    elif call.data == 'genres_family':
        movies = imdb.SearchByGenres('family')
    elif call.data == 'genres_fun':
        movies = imdb.SearchByGenres('comedy')
    elif call.data == 'genres_animation':
        movies = imdb.SearchByGenres('animation')
    elif call.data == 'genres_scifi':
        movies = imdb.SearchByGenres('sci_fi')
    elif call.data == 'genres_horror':
        movies = imdb.SearchByGenres('horror')
    elif call.data == 'genres_inlove':
        movies = imdb.SearchByGenres('romance')
    else:
        bot.send_message(chat_id, 'No Genre')

    Create_Movie_Result(chat_id, movies)
    

@bot.callback_query_handler(func=lambda call: call.data.startswith('movie_'))
def Movie_Genre_Details(call):
    movie_Id= call.data.split("_")[1]
    chat_id = call.from_user.id
    movie = imdb.GetMovieDetails(movie_Id)
    trailer = movie['trailer']['link']
    image = ''
    if 'None' not in item['image']:
        image = item['image']
    movie_type= movie['type']
    caption = ''' 
     Title: {0} \n\nYear : {1} \n\nType : {2} \n\nActors : {3} \n\nStory : {4}
     '''.format(movie['fullTitle'], movie['year'], movie_type, movie['stars'], movie['plot'])
    keyboards = InlineKeyboardMarkup(row_width=3)
    search_agin = InlineKeyboardButton(text= "Search agin", callback_data="/search" )
    watch_trailer = InlineKeyboardButton(text= "Watch Trailer", url=trailer )
    keyboards.add(search_agin, watch_trailer)
    if image  == '':
        bot.send_message(chat_id, caption , reply_markup=keyboards)
    else:
        bot.send_photo(chat_id, image, reply_markup=keyboards, caption=caption)


@bot.callback_query_handler(func=lambda call: call.data.startswith('gpt_'))
def Movie_Genre_Details(call):
    movie_text= call.data.split("_")[1]
    chat_id = call.from_user.id
    movies = imdb.SearchByTitle(movie_text)
    if len(movies) == 0:
        bot.register_next_step_handler("No Movie!!!", Search_Error_Handler)
    else:
        for item in movies:
            keyboard = InlineKeyboardMarkup()
            title = item['title']
            _id = item['id']
            description = item['description']
            if 'None' not in item['image']:
                thumb_url = item['image']
            button = InlineKeyboardButton(text=title, callback_data="movie_{0}".format(_id))
            keyboard.add(button)
            bot.send_photo(chat_id, thumb_url,caption=title, reply_markup=keyboard)


def Movie_Search_Details(message):
    movie_Id= message.text.split("_")[1]
    chat_id = message.chat.id
    movie = imdb.GetMovieDetails(movie_Id)
    trailer = movie['trailer']['link']
    image = movie['image']
    movie_type=movie['type']
    caption = ''' 
    Title: {0} \n\nYear : {1} \n\nType : {2} \n\nActors : {3} \n\nStory : {4}
    '''.format(movie['fullTitle'], movie['year'], movie_type, movie['stars'], movie['plot'])
    keyboards = InlineKeyboardMarkup(row_width=3)
    search_agin = InlineKeyboardButton(text= "Search agin", switch_inline_query_current_chat='' )
    watch_trailer = InlineKeyboardButton(text= "Watch Trailer", url=trailer )
    keyboards.add(search_agin, watch_trailer)
    bot.send_photo(chat_id, image, reply_markup=keyboards, caption=caption)


@bot.callback_query_handler(func=lambda call: True)
def Call_Back_Handler(call):
    if call.data == '/search':
        Search(call.message)
    elif call.data == '/genres':
        Genres(call.message)
    elif call.data == '/gptsuggest':
        GPT_Search(call.message)
    elif call.data == '/about':
        About(call.message)


@bot.message_handler(func=lambda message: message.text.startswith('movie_'))
def MovieHandler(message):
    Movie_Search_Details(message)


@bot.message_handler(func=lambda message: True)
def echo_message(message):
    chat_id = message.chat.id
    Help(message)


def Search_Error_Handler(message):
    keyboards = InlineKeyboardMarkup()
    search = InlineKeyboardButton(text="Search Movie", switch_inline_query_current_chat='')
    genres = InlineKeyboardButton(text="Search by Genres", callback_data="/genres")
    gpt = InlineKeyboardButton(text="Chat GPT", callback_data="/gptsuggest")
    keyboards.add(search, genres, gpt)
    bot.send_message(message.chat.id, "Try Agin:", reply_markup=keyboards)