��    ,      |  ;   �      �     �     �     �               $     =     L     a     u     �     �     �     �     �          #     /     D     X     u     �  
   �     �     �     �     �                0     ?     U     g     �     �     �     �  
   �     �        	             +  �  ?  f   �  b   G	  o   �	  }  
  �   �  )   7      a  �   �  }     �   �  �   <  �   �  �   s  c     f   {  �   �  w   {  S   �  ~   G  �   �  z   `  �   �  @  f  �  �  u  J  J   �  q     �   }  .   �     -  B   :  �   }  7   *  �   b  K   (  E   t  I   �  �        �   v   �!  �   Z"  �   �"  �   �#     $                !   ,                          (                   *             #                          	          +                 "      
             %   )                   &   '                 blackout.format blackout.format_addressless blackout.format_md help.line_1 kirov.reporting list.addresses_you_watch main.cancelled main.unknown_command notify.desc_changed notify.desc_changed_multiple notify.details notify.details_again notify.details_again_multiple notify.details_changed notify.details_changed_multiple notify.details_multiple notify.done notify.done_multiple notify.time_changed notify.time_changed_multiple notify.type_changed notify.type_changed_multiple start.done start.done_with_blackouts stats.details status.current_blackouts status.no_blackouts status.nothing_is_watched unwatch.aaaargh unwatch.cancel unwatch.choose_wisely unwatch.not_found unwatch.nothing_to_unwatch unwatch.removed watch.already_watching watch.blocked_or_broken watch.choose_your_destiny watch.done watch.done_with_blackouts watch.not_expected watch.wat watch.welcome watch.wrong_address Project-Id-Version: 
POT-Creation-Date: 2017-08-06 01:15+1000
PO-Revision-Date: 2017-08-06 01:44+1000
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
{type_emoji} {type_nominative_capitalized} (#off{id})
📅 {date}
🕓 {time}
🗒 {desc} [{type_emoji} {type_nominative_capitalized}]({url}) (#off{id})
📅 {date}
🕓 {time}
🗒 {desc} {addresses}:
[{type_emoji} {type_nominative_capitalized}]({url}) (#off{id})
📅 {date}
🕓 {time}
🗒 {desc} Бот присылает уведомления об отключениях коммунальных услуг по выбранным адресам Владивостока.
Для того, чтобы наблюдать за домом, добавьте его в список с помощью команды /watch
Чтобы перестать наблюдать за домом, удалите его из списка с помощью команды /unwatch
Чтобы получить ваш список наблюдения, воспользуйтесь командой /list
Чтобы узнать состояние всех домов, за которыми вы следите, используйте команду /status
Если что-то пошло не так и вы запутались, используйте /cancel чтобы отменить команду. Кажется, что-то пошло не так, как задумывалось. Мы уже знаем об этом и скоро всё починим. Ваш список наблюдения: Команда отменена. Неизвестная команда. Воспользуйтесь справкой с помощью команды /help@vloffbot Изменено описание [отключения {type} №{id}]({url}) по адресу {addresses}: {desc} #off{id} Изменено описание [отключения {type} №{id}]({url}): {desc}. Отключение затрагивает дома по адресам

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
#off{id} Здравствуйте. Бот будет следить за отключениями по адресу {addresses}. Если вы хотите добавить больше адресов и узнать обо всех возможностях бота, воспользуйтесь командой /help@vloffbot. Здравствуйте. Бот будет следить за отключениями по адресу {addresses}. Если вы хотите добавить больше адресов и узнать обо всех возможностях бота, воспользуйтесь командой /help@vloffbot.

Сейчас по этому адресу зарегистрированы отключения: ```
Новые пользователи (чаты) / Новые подписки (в чатах) / Пользователи (чаты) без подписки
За 24 часа: {daily[0]:>4} ({daily[1]:>4}) / {daily[2]:>4} ({daily[3]:>4}) / {daily[4]:>4} ({daily[5]:>4})
За неделю:  {weekly[0]:>4} ({weekly[1]:>4}) / {weekly[2]:>4} ({weekly[3]:>4}) / {weekly[4]:>4} ({weekly[5]:>4})
За месяц:   {monthly[0]:>4} ({monthly[1]:>4}) / {monthly[2]:>4} ({monthly[3]:>4}) / {monthly[4]:>4} ({monthly[5]:>4})
Всего:      {total[0]:>4} ({total[1]:>4}) / {total[2]:>4} ({total[3]:>4}) / {total[4]:>4} ({total[5]:>4})``` Отключения в домах из списка наблюдения: В домах, за которыми вы наблюдаете, нет актуальных отключений. В списке наблюдения нет домов. Добавьте дом с помощью команды /watch@vloffbot Выберите адрес из списка. Отмена Какой адрес нужно удалить из списка? Нельзя удалить адрес, за которым вы не наблюдаете. Выберите адрес из вашего списка наблюдения. В списке наблюдения нет домов. Адрес удален из списка наблюдения. Вы больше не будете получать уведомления об отключениях по этому адресу. Этот адрес уже в вашем списке наблюдения. Неправильный адрес. Попробуйте снова. Выберите дом, за которым хотите следить: Адрес добавлен в список наблюдения. Вы будете получать уведомления о новых отключениях по этому адресу. Адрес добавлен в список наблюдения. Вы будете получать уведомления о новых отключениях по этому адресу. Сейчас по этому адресу зарегистрированы отключения: Не понимаю, о чем вы. Пришлите адрес текстом или местоположением. Я не могу понять, о чем вы. Отправьте адрес, за которым вы хотите наблюдать. Пришлите адрес, за которым вы хотите наблюдать. Вы можете отправить его текстом (например, Алеутская 65) или местоположением. Не могу найти этот адрес. Пожалуйста, пришлите корректный адрес текстом (например, Алеутская 65) или местоположением. 