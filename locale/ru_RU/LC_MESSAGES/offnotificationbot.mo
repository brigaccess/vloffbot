��    (      \  5   �      p     q     �     �     �     �     �     �     �     
     '     6     K     i     �     �     �     �     �     �     
          ;     T     h     �     �     �     �     �     �     �          #  
   =     H     b  	   u          �  �  �  o   B  b   �  �  	  �   �  )   _      �  �   �  }   /  �   �  �   d  �   �  �   �  c   ?  f   �  �   
  w   �  S     ~   o  �   �  z   �  �     J   �  q   �  �   K  .   �     �  B     �   K  7   �  �   0  K   �  E   B  I   �  �   �    �  v   �  �   (  �   �  �   �                                    !               (                                '   $                   	             
       %                      &                #      "       blackout.format blackout.format_addressless help.line_1 kirov.reporting list.addresses_you_watch main.cancelled main.unknown_command notify.desc_changed notify.desc_changed_multiple notify.details notify.details_again notify.details_again_multiple notify.details_changed notify.details_changed_multiple notify.details_multiple notify.done notify.done_multiple notify.time_changed notify.time_changed_multiple notify.type_changed notify.type_changed_multiple status.current_blackouts status.no_blackouts status.nothing_is_watched unwatch.aaaargh unwatch.cancel unwatch.choose_wisely unwatch.not_found unwatch.nothing_to_unwatch unwatch.removed watch.already_watching watch.blocked_or_broken watch.choose_your_destiny watch.done watch.done_with_blackouts watch.not_expected watch.wat watch.welcome watch.wrong_address Project-Id-Version: 
POT-Creation-Date: 2017-06-24 07:47+1000
PO-Revision-Date: 2017-06-24 08:38+1000
Last-Translator: 
Language-Team: 
Language: ru_RU
MIME-Version: 1.0
Content-Type: text/plain; charset=UTF-8
Content-Transfer-Encoding: 8bit
Generated-By: pygettext.py 1.5
X-Generator: Poedit 2.0.1
Plural-Forms: nplurals=3; plural=(n%10==1 && n%100!=11 ? 0 : n%10>=2 && n%10<=4 && (n%100<10 || n%100>=20) ? 1 : 2);
 {addresses}:
[{type_emoji} {type_nominative_capitalized}]({url}) (#off{id})
📅 {date}
🕓 {time}
🗒 {desc} [{type_emoji} {type_nominative_capitalized}]({url}) (#off{id})
📅 {date}
🕓 {time}
🗒 {desc} Бот присылает уведомления об отключениях коммунальных услуг по выбранным адресам Владивостока.
Для того, чтобы наблюдать за домом, добавьте его в список с помощью команды /watch@vloffbot
Чтобы перестать наблюдать за домом, удалите его из списка с помощью команды /unwatch@vloffbot
Чтобы получить ваш список наблюдения, воспользуйтесь командой /list@vloffbot
Чтобы узнать состояние всех домов, за которыми вы следите, используйте команду /status@vloffbot
Если что-то пошло не так и вы запутались, используйте /cancel@vloffbot чтобы отменить команду. Кажется, что-то пошло не так, как задумывалось. Мы уже знаем об этом и скоро всё починим. Ваш список наблюдения: Команда отменена. Неизвестная команда. Воспользуйтесь справкой с помощью команды /help@vloffbot Изменено описание [отключения {type} №{id}]({url}) по адресу {addresses}: {desc} #off{id} Изменено описание [отключения {type} №{id}]({url}): {desc}. Отключение затрагивает дома по адресам

{addresses}
#off{id} {type_emoji} {type_capitalized} по адресу {addresses} не будет {date} {time}

([отключение №{id}]({url}), {desc}) #off{id} {type_emoji} {type_capitalized} по адресу {addresses} снова не будет {date} {time}

([отключение №{id}]({url}), {desc}) #off{id} {type_emoji} {type_capitalized} снова не будет {date} {time} по адресам:

{addresses}
([отключение №{id}]({url}), {desc}) #off{id} Изменены детали [отключения №{id}]({url}) по адресу {addresses}:  Изменены детали [отключения №{id}]({url}) по адресам: 

{addresses} {type_emoji} {type_capitalized} не будет {date} {time} по адресам:

{addresses}
([отключение №{id}]({url}), {desc}) #off{id} {type_emoji} {type_capitalized} дали по адресу {addresses} ([отключение №{id}]({url})) #off{id} {type_emoji} {type_capitalized} дали по адресам

{addresses} 
#off{id} Изменены сроки [отключения {type} №{id}]({url}) по адресу {addresses}: {date} {time} #off{id} Изменены сроки [отключения {type} №{id}]({url}): {type} не будет {date} {time} по адресам 

{addresses}
#off{id} Изменен тип [отключения №{id}]({url}): по адресу {addresses} не будет {type} #off{id} Изменен тип [отключения №{id}]({url}): теперь не будет {type} по адресам

{addresses}
#off{id} Отключения в домах из списка наблюдения: В домах, за которыми вы наблюдаете, нет актуальных отключений. В списке наблюдения нет домов. Добавьте дом с помощью команды /watch@vloffbot Выберите адрес из списка. Отмена Какой адрес нужно удалить из списка? Нельзя удалить адрес, за которым вы не наблюдаете. Выберите адрес из вашего списка наблюдения. В списке наблюдения нет домов. Адрес удален из списка наблюдения. Вы больше не будете получать уведомления об отключениях по этому адресу. Этот адрес уже в вашем списке наблюдения. Неправильный адрес. Попробуйте снова. Выберите дом, за которым хотите следить: Адрес добавлен в список наблюдения. Вы будете получать уведомления о новых отключениях по этому адресу. Адрес добавлен в список наблюдения. Вы будете получать уведомления о новых отключениях по этому адресу. Сейчас по этому адресу зарегистрированы отключения: Не понимаю, о чем вы. Пришлите адрес текстом или местоположением. Я не могу понять, о чем вы. Отправьте адрес, за которым вы хотите наблюдать. Пришлите адрес, за которым вы хотите наблюдать. Вы можете отправить его текстом (например, Алеутская 65) или местоположением. Не могу найти этот адрес. Пожалуйста, пришлите корректный адрес текстом (например, Алеутская 65) или местоположением. 