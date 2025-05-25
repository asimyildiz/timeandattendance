import pandas as pd
from datetime import datetime, timedelta

def read_excel_data(filepath):
    dataframe = pd.read_excel(filepath, header=2, engine='openpyxl')
    dataframe = dataframe[dataframe['Hrs.'] != 0]
    dataframe = dataframe[dataframe['Hrs.'].notna()]
    dataframe['Date'] = pd.to_datetime(dataframe.iloc[:, 0], format="%d-%b-%y", errors='coerce')
    dataframe = dataframe[dataframe['Date'].notna()]
    return dataframe
    
def extract_row_fields(row, dataframe):
    date = row['Unnamed: 0']
    start_time = row['Unnamed: 3']
    leave_time = row['Unnamed: 4']
    schedule_hours = str(row['Hrs.'])
    total_in = str(row['In Time']).replace("-", "0")
    total_out = str(row['Out Time']).replace("-", "0")
    total_overall = row['Exception Recorded']
    note = str(row['Unnamed: 44']).replace("nan", "")
    additional_sum = sum(
        float(row[col]) for col in dataframe.columns[9:42]
        if pd.notna(row[col])
    )
    return date, start_time, leave_time, schedule_hours, total_in, total_out, total_overall, note, additional_sum

def extract_employee_info(filepath):
    excel_file = pd.ExcelFile(filepath, engine='openpyxl')
    first_row = excel_file.book.active['A1'].value
    employee_number, employee_name = first_row.replace("Daily View of ", "").split(" - ")
    return employee_number, employee_name

def calculate_timedelta(schedule_hours):
    try:
        hours_minutes = float(schedule_hours)
        hours = int(hours_minutes)
        minutes = int(round((hours_minutes - hours) * 60))
        return timedelta(hours=hours, minutes=minutes)
    except:
        return timedelta()

def parse_times(start_time, leave_time):
    try:
        start_ptime = datetime.strptime(start_time, "%H:%M").time()
        leave_ptime = datetime.strptime(leave_time, "%H:%M").time()
        return start_ptime, leave_ptime
    except ValueError:
        return None, None
    
def get_date(date):
    try:
        date_str = pd.to_datetime(date).strftime("%d-%b-%y")
    except:
        date_str = str(date)
    return date_str
    
def compute_inout_total(total_in, total_out, additional_sum):
    try:
        inout_value = float(total_in) + float(total_out) + float(additional_sum)
        inout_hours = int(inout_value)
        inout_minutes = int(round((inout_value - inout_hours) * 60))
        return timedelta(hours=inout_hours, minutes=inout_minutes)
    except:
        return timedelta()

def compute_out_total(total_out, additional_sum):
    try:
        out_value = float(total_out) - float(additional_sum)
        out_hours = int(out_value)
        out_minutes = int(round((out_value - out_hours) * 60))
        return timedelta(hours=out_hours, minutes=out_minutes)
    except:
        return None
    
def check_entry_exit(start_ptime, leave_ptime, exception_details):
    if start_ptime > datetime.strptime("08:30", "%H:%M").time():
        exception_details['LATE_ENTRY'] = start_ptime
    
    if start_ptime < datetime.strptime("06:00", "%H:%M").time() and leave_ptime < datetime.strptime("14:30", "%H:%M").time():
        exception_details["EARLY_ENTRY"] = f"{start_ptime} - {leave_ptime}"

def check_in_time(inout_total, schedule_hours, exception_details):
    if inout_total < calculate_timedelta(schedule_hours):
        missing = calculate_timedelta(schedule_hours) - inout_total
        if missing > timedelta(minutes=30):
            exception_details["LESS_ENTRY"] = missing

def check_out_time(total_out, additional_sum, exception_details):
    if not pd.isna(total_out):
        out_total = compute_out_total(total_out, additional_sum)
        if out_total and out_total > timedelta(hours=1):
            exception_details["TOTAL_OUT"] = out_total - timedelta(hours=1)
            
def check_missing_day(start_time, additional_sum, schedule_hours, exception_details):
    if pd.isna(start_time) and additional_sum == 0.0:
        missing = calculate_timedelta(schedule_hours)
        exception_details["MISSING_DAY"] = missing

def evaluate_exceptions(date, start_time, leave_time, schedule_hours, total_in, total_out, total_overall, note, additional_sum):
    exception_details = {
        "DATE": get_date(date),
        "LATE_ENTRY": None,
        "EARLY_ENTRY": None,
        "LESS_ENTRY": None,
        "TOTAL_OUT": None,
        "MISSING_DAY": None,
        "NOTE": note
    }
    
    if not (pd.isna(start_time) or pd.isna(leave_time) or pd.isna(total_overall)):
        start_ptime, leave_ptime = parse_times(start_time, leave_time)
        if not start_ptime or not leave_ptime:
            return exception_details

        inout_total = compute_inout_total(total_in, total_out, additional_sum)
        check_entry_exit(start_ptime, leave_ptime, exception_details)
        check_in_time(inout_total, schedule_hours, exception_details)
        check_out_time(total_out, additional_sum, exception_details)

        if schedule_hours == "8":
            exception_details["NOTE"] += " FRIDAY, VALIDATE IF MUSLIM"

    check_missing_day(start_time, additional_sum, schedule_hours, exception_details)
    return exception_details

    
def analyze_row(row, dataframe):
    date, start_time, leave_time, schedule_hours, total_in, total_out, total_overall, note, additional_sum = extract_row_fields(row, dataframe)
    return evaluate_exceptions(
        date, start_time, leave_time, schedule_hours, total_in, total_out, total_overall, note, additional_sum
    )

def calculate_total_missing(exceptions):
    total_missing_keys = {"LESS_ENTRY", "TOTAL_OUT", "MISSING_DAY"}
    time_deltas = (
        exc[key]
        for exc in exceptions
        for key in total_missing_keys
        if key in exc and exc[key] is not None
    )
    return sum(time_deltas, timedelta(0))

def calculate_total_early_entries(exceptions):
    return sum(1 for item in exceptions if item.get("EARLY_ENTRY") is not None)

def calculate_total_late_entries(exceptions):
    return sum(1 for item in exceptions if item.get("LATE_ENTRY") is not None)

def check_for_any_exception_per_day(exceptions):
    return all(v is None for k, v in exceptions.items() if k != "DATE" and k != "NOTE")

def parse_excel(filepath):
    dataframe = read_excel_data(filepath)
    employee_number, employee_name = extract_employee_info(filepath)

    first_date = dataframe['Date'].iloc[-1].strftime("%d-%b-%y")
    last_date = dataframe['Date'].iloc[0].strftime("%d-%b-%y")

    exceptions = []
    total_number_of_days = 0
    total_annual_leave = 0.0
    total_sick_leave = 0.0

    for _, row in dataframe.iterrows():
        total_number_of_days += 1
        total_annual_leave += float(row['LV'])
        total_sick_leave += float(row['I'])

        exception_details = analyze_row(row, dataframe)
        if not check_for_any_exception_per_day(exception_details):
            exceptions.append(exception_details)

    total_missing_hours = calculate_total_missing(exceptions)
    total_number_of_early_entries = calculate_total_early_entries(exceptions)
    total_number_of_late_entries = calculate_total_late_entries(exceptions)

    # generate message as well
    message = generate_employee_message(employee_number, employee_name, total_number_of_early_entries, total_number_of_late_entries, first_date, last_date, total_number_of_days, total_missing_hours)

    # print_summary(employee_number, employee_name, exceptions, first_date, last_date, total_number_of_days, total_number_of_early_entries, total_number_of_late_entries, total_missing_hours, total_annual_leave, total_sick_leave)

    return {
        "employee_number": employee_number, 
        "employee_name": employee_name, 
        "exceptions": exceptions, 
        "first_date": first_date, 
        "last_date": last_date,
        "total_number_of_days": total_number_of_days, 
        "total_number_of_early_entries": total_number_of_early_entries, 
        "total_number_of_late_entries": total_number_of_late_entries,
        "total_missing_hours": total_missing_hours, 
        "total_annual_leave": total_annual_leave, 
        "total_sick_leave": total_sick_leave, 
        "message": message
    }

def generate_employee_message(employee_number, employee_name, total_number_of_early_entries, total_number_of_late_entries, first_date, last_date, total_number_of_days, total_missing_hours):
    message = f"Dear {employee_number} - {employee_name},</br></br>"
    message += f"Your attendance record has been reviewed for the period from <b>{first_date}</b> to <b>{last_date}</b>, covering <b>{total_number_of_days} working days</b>.</br></br>"

    if total_number_of_early_entries > 0:
        message += f"- You have <b>{total_number_of_early_entries} early entries</b> during this period. All employees are expected to arrive between <b>06:00 and 08:30</b>, and complete their minimum required hours (8.5 hours between Monday to Thursday, 8 hours on Fridays).</br>"
    
    # Handle late entries
    if total_number_of_late_entries > 0:
        message += f"- You have <b>{total_number_of_late_entries} late entries</b> during this period. All employees are expected to arrive between <b>06:00 and 08:30</b>, and complete their minimum required hours (8.5 hours between Monday to Thursday, 8 hours on Fridays).</br>"
    
    if total_number_of_early_entries == 0 and total_number_of_late_entries == 0:
        message += "- Great job! You have <b>no early/late entries</b> during this period. Your punctuality is appreciated.</br>"

    # Handle missing hours
    if total_missing_hours:
        message += f"- You have accumulated approximately <b>{total_missing_hours} hours of missing time</b>. Please submit a leave request to cover this, preferably from the day with the <b>most missing hours</b>.</br>"
    else:
        message += "- You have <b>no missing working hours</b>. Thank you for maintaining full attendance.</br>"

    # Final note
    if total_number_of_late_entries > 0 or total_missing_hours:
        message += (
            "</br>We kindly remind you to <b>follow company attendance policies consistently</b>. "
            "Further deviations may lead to a <b>formal written warning</b>.</br>"
        )
    else:
        message += "Keep up the excellent attendance and dedication to your responsibilities.</br>"

    message += "</br>Best regards"

    return message

def print_summary(employee_number, employee_name, exceptions, first_date, last_date, total_number_of_days, total_number_of_early_entries, total_number_of_late_entries, total_missing_hours, total_annual_leaves, total_sick_leaves):
    print("=" * 50)
    print(f"Summary for {employee_number} - {employee_name}")
    print("=" * 50)
    for item in exceptions:
        print(f"{item['DATE']} - {item['LATE_ENTRY']} - {item['EARLY_ENTRY']} - {item['LESS_ENTRY']} - {item['TOTAL_OUT']} - {item['MISSING_DAY']}")
    print("=" * 50)
    print(f"Time Frame: {first_date} - {last_date}")
    print(f"Total Number of Days Processed: {total_number_of_days}")
    print(f"Total Number of Early Entries: {total_number_of_early_entries}")    
    print(f"Total Number of Late Entries: {total_number_of_late_entries}")    
    print(f"Total Missing Hours: {total_missing_hours}")
    print(f"Total Annual Leave in Hours: {str(total_annual_leaves)}")
    print(f"Total Sick Leave in Hours: {str(total_sick_leaves)}")
    print("=" * 50)
