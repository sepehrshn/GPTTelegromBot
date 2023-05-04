import telebot
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup, InlineQueryResultArticle, InputTextMessageContent, ForceReply
import Core.IMDB.IMDB_API_URL as imdb
import Core.GPT.GPT as gpt

telegramToken = '6054329768:AAHO04PQvG3xwY47Y1BCik78USwbSDGoLIU'

bot = telebot.TeleBot(telegramToken)


@bot.message_handler(commands=['start'])
def Wellcome_Message(message):
    keyboard = InlineKeyboardMarkup(row_width=3)
    search_button = InlineKeyboardButton(text="جستجو فیلم", callback_data="/search")
    genres_button = InlineKeyboardButton(text="ژانر فیلم", callback_data="/genres")
    gpt_button = InlineKeyboardButton(text="پیشنهاد ChatGPT", callback_data="/gptsuggest")
    filoger_button = InlineKeyboardButton(text="مدرسه فیلاگر", url="https://filoger.com")
    about_button = InlineKeyboardButton(text="درباره ربات", callback_data="/about")
    keyboard.add(search_button, genres_button, gpt_button, filoger_button, about_button)
    bot.send_message(message.chat.id, """
    به ربات IMDB خوش آمدید.
    شما می توانید نام فیلم مورد نظر خودتان را سرچ کنید یا با انتخاب ژانر دلخواه می توانید پیشنهادات ما را ببینید و یا می توانید به کمک ChatGPT پیشنهاد های ویژه در یافت کنید.
    با ما همراه باشید.
    """, reply_markup=keyboard)


@bot.message_handler(commands=['help'])
def Help(message):
    keyboard = InlineKeyboardMarkup(row_width=3)
    search_button = InlineKeyboardButton(text="جستجو فیلم", callback_data="/search",switch_inline_query_current_chat='@' + bot.get_me().username)
    genres_button = InlineKeyboardButton(text="ژانر فیلم", callback_data="/genres")
    gpt_button = InlineKeyboardButton(text="پیشنهاد ChatGPT", callback_data="/gptsuggest")
    filoger_button = InlineKeyboardButton(text="مدرسه فیلاگر", url="https://filoger.com")
    keyboard.add(search_button, genres_button, gpt_button, filoger_button)
    bot.send_message(message.chat.id, """
    با انتخاب یکی از گزینه های زیر میتوانید از امکانات بات استفاده کنید!
    """, reply_markup=keyboard)


@bot.message_handler(commands=['gptsuggest'])
def GPT_Search(message):
    chat_id = message.chat.id
    replay_message = bot.send_message(chat_id, 'تم فیلمی که دوست دارید را مانند نمونه وارد کنید(old man in farm, ...):')
    bot.register_next_step_handler(replay_message, GPT_Suggest_Result)


@bot.message_handler(commands=['search'])
def Search(message):
    chat_id = message.chat.id
    replay_message = bot.send_message(chat_id, 'نام فیلم مورد نظر خود را وارد کنید:',reply_markup=markup)
    bot.register_next_step_handler(replay_message, Movie_with_Search)


@bot.message_handler(commands=['genres'])
def Genres(message):
    keyboard = InlineKeyboardMarkup(row_width=3)
    action = InlineKeyboardButton(text="اکشن", callback_data="genres_action")
    drama = InlineKeyboardButton(text="درام", callback_data="genres_drama")
    family = InlineKeyboardButton(text="خانوادگی", callback_data="genres_family")
    fun = InlineKeyboardButton(text="کمدی", callback_data="genres_fun")
    animation = InlineKeyboardButton(text="انیمیشن", callback_data="genres_animation")
    scifi = InlineKeyboardButton(text="علمی و تخیلی", callback_data="genres_scifi")
    horror = InlineKeyboardButton(text="ترسناک", callback_data="genres_horror")
    inLove = InlineKeyboardButton(text="عاشقانه", callback_data="genres_inlove")
    keyboard.add(action, drama, family, fun, animation, scifi, horror, inLove)
    bot.send_message(message.chat.id, """ژانر مورد علاقه خود را انتخاب کنید:""", reply_markup=keyboard)


@bot.inline_handler(lambda query: len(query.query) > 0)
def Movie_with_Search(query):
    results = []
    text = query.query
    if query.query.startswith('gpt:'):
        gpt.Suggestion(text)
    if len(text)>3 :
        movies = imdb.SearchByTitle(text)
        if movies is not None:
            for item in movies:
                article = InlineQueryResultArticle(
                    id=item['id'],
                    title=item['title'],
                    description=item['description'],
                    input_message_content= InputTextMessageContent(message_text = "movie_{0}".format(item['id'])),
                    thumbnail_url=item['image']
                )
                results.append(article)
            bot.answer_inline_query(query.id, results)
        else:
            article = InlineQueryResultArticle(title='فیلمی یافت نشد')
            bot.answer_inline_query(query.id, article)


def GPT_Suggest_Result(message):
    text = message.text
    movies = gpt.Suggestion(text)
    keyboard = InlineKeyboardMarkup()
    for item in movies:
        button = InlineKeyboardButton(text=item, callback_data="gpt_{0}".format(item))
        keyboard.add(button)
    bot.send_message(message.chat.id, 'لیست فیلم های پیشنهادی:' ,reply_markup=keyboard)


def Create_Movie_Result(id, movies):
    if len(movies) == 0:
        bot.register_next_step_handler("فیلم مورد نظر یافت نشد!!!", Search_Error_Handler)
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
        bot.send_message(chat_id, 'ژانر مورد نظر یافت نشد')

    Create_Movie_Result(chat_id, movies)
    

@bot.callback_query_handler(func=lambda call: call.data.startswith('movie_'))
def Movie_Genre_Details(call):
    movie_Id= call.data.split("_")[1]
    chat_id = call.from_user.id
    movie = imdb.GetMovieDetails(movie_Id)
    trailer = movie['trailer']['link']
    image = movie['image']
    movie_type=''
    if movie['type'].lower() =='tvseries':
        movie_type = 'سریال'
    elif movie['type'].lower() =='movie':
        movie_type = 'سینمایی'
    else:
        movie_type = movie['type'].lower()
    caption = ''' 
     نام فیلم : {0} \n\nسال تولید : {1} \n\nنوع : {2} \n\nبازیگران : {3} \n\nداستان : {4}
     '''.format(movie['fullTitle'], movie['year'], movie_type, movie['stars'], movie['plot'])
    keyboards = InlineKeyboardMarkup(row_width=3)
    search_agin = InlineKeyboardButton(text= "جستجوی مجدد", callback_data="/search" )
    watch_trailer = InlineKeyboardButton(text= "تماشای تریلر", url=trailer )
    keyboards.add(search_agin, watch_trailer)
    bot.send_photo(chat_id, image, reply_markup=keyboards, caption=caption)


@bot.callback_query_handler(func=lambda call: call.data.startswith('gpt_'))
def Movie_Genre_Details(call):
    movie_text= call.data.split("_")[1]
    chat_id = call.from_user.id
    movies = imdb.SearchByTitle(movie_text)
    if len(movies) == 0:
        bot.register_next_step_handler("فیلم مورد نظر یافت نشد!!!", Search_Error_Handler)
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
    movie_type=''
    if movie['type'].lower() =='tvseries':
        movie_type = 'سریال'
    elif movie['type'].lower() =='movie':
        movie_type = 'سینمایی'
    else:
        movie_type = movie['type'].lower()
    caption = ''' 
    نام فیلم : {0} \n\nسال تولید : {1} \n\nنوع : {2} \n\nبازیگران : {3} \n\nداستان : {4}
    '''.format(movie['fullTitle'], movie['year'], movie_type, movie['stars'], movie['plot'])
    keyboards = InlineKeyboardMarkup(row_width=3)
    search_agin = InlineKeyboardButton(text= "جستجوی مجدد", callback_data="/search" )
    watch_trailer = InlineKeyboardButton(text= "تماشای تریلر", url=trailer )
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


@bot.message_handler(func=lambda message: message.text.startswith('movie_'))
def MovieHandler(message):
    Movie_Search_Details(message)


@bot.message_handler(func=lambda message: True)
def echo_message(message):
    chat_id = message.chat.id
    Help(message)


def Search_Error_Handler(message):
    keyboards = InlineKeyboardMarkup()
    search = InlineKeyboardButton(text="جستجو فیلم دلخواه", callback_data="/search")
    genres = InlineKeyboardButton(text="جستجو براساس ژانر", callback_data="/genres")
    gpt = InlineKeyboardButton(text="پیشنهاد ChatGPT", callback_data="/gptsuggest")
    keyboards.add(search, genres, gpt)
    bot.send_message(message.chat.id, "دوباره امتحان کنید:", reply_markup=keyboards)