def format_blackout(s, address, blackout):
    return s.format(
            address=address.address, blackout_id=blackout.id,
            blackout_type=blackout.type_, blackout_date=blackout.date_,
            blackout_time=blackout.time_, blackout_desc=blackout.description
            )
