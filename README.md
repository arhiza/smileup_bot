# Простой телеграм-бот на вебхуках

В папке smileup:

* В urls задаем адрес, на который сервер телеграма будет присылать сообщения. Адрес не должен храниться в коде, а может быть спрятан в базу данных или в переменную окружения.

* Во views проверяем, что post-запрос пришел на правильный адрес, обрабатываем сообщение, и возвращаем статус 200 (либо телеграм будет присылать то же сообщение до бесконечности, пока не получит желаемого ответа).

* В bot функции для обработки сообщения - разбираем json с данными, выясняем, от кого и что получено, делаем какие-либо действия.


@smileup_bot - бот работающий, хранит цитаты из книжек


---
## импорт-экспорт данных
сохранить содержимое таблиц пользователей и цитат в файл в корне проекта:

`python3.6 manage.py dumpdata smileup.BotUser smileup.Post --format json -o smileup.json`

загрузка данных обратно в базу:

`python manage.py loaddata smileup.json`