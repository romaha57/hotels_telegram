from telegram_bot_calendar import DetailedTelegramCalendar


def get_calendar(is_process=False, callback_data=None, **kwargs):
    if is_process:
        result, key, step = DetailedTelegramCalendar(calendar_id=kwargs.get('calendar_id'),
                                                     current_date=kwargs.get('current_date'),
                                                     min_date=kwargs.get('min_date'),
                                                     locale=kwargs.get('locale')).process(callback_data.data)
        return result, key, step
    else:
        calendar, step = DetailedTelegramCalendar(calendar_id=kwargs.get('calendar_id'),
                                                  current_date=kwargs.get('current_date'),
                                                  min_date=kwargs.get('min_date'),
                                                  locale=kwargs.get('locale')).build()
        return calendar, step