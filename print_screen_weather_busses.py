from waveshare_epd import epd7in5_V2
import datetime
from get_weather import get_weather_info
from get_hafas import get_bus_departure_info
from icons_arrays import cloud_icon, sun_rain_icon, sun_icon, rain_icon, sun_cloud_icon
from helvetica_bitmap import font  # your generated font
from achtkugel import magische_acht_kugel   # Magic Eightball import
from icons_arrays_eightball import eightball_ja_icon, eightball_no_icon  # Icons für Ja/Nein

# === Display helpers ===
def draw_char_scaled(buffer, char, x, y, width, scale=1.0):
    if char not in font:
        char = " "
    bitmap = font[char]
    height = max(b.bit_length() for b in bitmap)
    for col_idx, col_val in enumerate(bitmap):
        for row in range(height):
            if (col_val >> row) & 1:
                block_size = max(int(round(scale)),1)
                for dx in range(block_size):
                    for dy in range(block_size):
                        px = int(x + round(col_idx*scale) + dx)
                        py = int(y + round(row*scale) + dy)
                        if px >= width or py >= epd.height:
                            continue
                        index = int((px + py*width)//4)
                        shift = int((3 - (px % 4))*2)
                        buffer[index] &= ~(0x03 << shift)

def draw_text_scaled(buffer,text,x,y,width,scale=1.0,spacing=1):
    x_offset = x
    for c in text:
        draw_char_scaled(buffer, c, x_offset, y, width, scale)
        char_width = len(font.get(c,[0]))
        x_offset += int(char_width*scale) + spacing

def draw_icon_inverted(buffer, icon_array, x_offset, y_offset, width):
    icon_size = 64
    for y in range(icon_size):
        for x in range(icon_size):
            px = x_offset + x
            py = y_offset + y
            if px >= width or py >= epd.height:
                continue
            val = icon_array[y][x]
            val = 0 if val else 1
            if val:
                index = int((px + py*width)//4)
                shift = int((3 - (px % 4))*2)
                buffer[index] &= ~(0x03 << shift)

def choose_icon(weather):
    cloud = weather.get('cloudiness',0)
    rain = weather.get('precipitation_mm',0)
    if rain > 0:
        if cloud < 50:
            return sun_rain_icon
        else:
            return rain_icon
    else:
        if cloud < 30:
            return sun_icon
        elif cloud < 70:
            return sun_cloud_icon
        else:
            return cloud_icon

def aggregate_forecast(hourly, start_hour, end_hour):
    temps=[]
    clouds=[]
    precip=[]
    for h in hourly:
        h_hour=int(h['time'][11:13])
        if start_hour <= h_hour <= end_hour:
            temps.append(h['temperature'])
            clouds.append(h['cloudiness'])
            precip.append(h['precipitation_mm'])
    if temps:
        avg_temp = sum(temps)/len(temps)
        avg_cloud = sum(clouds)/len(clouds)
        total_precip = sum(precip)
        return {'temperature':avg_temp,'cloudiness':avg_cloud,'precipitation_mm':total_precip}
    else:
        return {'temperature':0,'cloudiness':0,'precipitation_mm':0}

def format_delay(delay):
    if delay == "on time":
        return ""
    return delay.lstrip('+').replace(':00','').replace(' min','')

def clean_bus_line(line):
    return line.replace("Bus ","")

# === Main ===
epd = epd7in5_V2.EPD()
epd.init()

width = epd.width
height = epd.height
buffer_size = (width*height)//4
buffer = bytearray([0xFF]*buffer_size)

# === Weather ===
weather_data = get_weather_info()
current = weather_data['current_weather']
hourly = weather_data['hourly_forecast']

left_padding = 20

# Current weather
icon_current = choose_icon(current)
draw_icon_inverted(buffer, icon_current, left_padding, 0, width)
temp_str = f"{int(round(current['temperature']))}° ({int(round(current['windchill']))}°)"
draw_text_scaled(buffer, temp_str, left_padding + 70, 10, width, scale=1.5)

# Morning/noon/evening
periods = [('Morgens',6,11),('Mittags',12,17),('Abends',18,23)]
x_start = left_padding
y_start = 90
spacing = 100
for i,(label,start,end) in enumerate(periods):
    forecast = aggregate_forecast(hourly, start, end)
    icon = choose_icon(forecast)
    label_scale = 0.8
    label_width = sum(len(font.get(c,[0]))*label_scale+1 for c in label)
    x_label = x_start + i*spacing + (64 - label_width)//2
    draw_text_scaled(buffer,label,x_label,y_start-18,width,scale=label_scale)
    draw_icon_inverted(buffer,icon,x_start+i*spacing,y_start,width)
    temp_text = f"{int(round(forecast['temperature']))}°"
    draw_text_scaled(buffer,temp_text,x_start+i*spacing,y_start+60,width,scale=1.5)

# Date and weekday
now = datetime.datetime.now()
date_str = now.strftime("%d.%m.%Y")
weekday_de = ["Montag","Dienstag","Mittwoch","Donnerstag","Freitag","Samstag","Sonntag"][now.weekday()]
scale_date = 2.0
total_width_date = sum(len(font.get(c,[0]))*scale_date + 1 for c in date_str)
x_date = width - int(total_width_date) - 10
y_date = 10
draw_text_scaled(buffer,date_str,x_date,y_date,width,scale=scale_date)
total_width_weekday = sum(len(font.get(c,[0]))*scale_date + 1 for c in weekday_de)
x_weekday = width - int(total_width_weekday) - 10
y_weekday = y_date + int(max(b.bit_length() for b in font['0'])*scale_date) + 6
draw_text_scaled(buffer,weekday_de,x_weekday,y_weekday,width,scale=scale_date)

# Current time
bus_info = get_bus_departure_info()
current_time_str = bus_info['current_time']
x_time = x_weekday + 22
y_time = y_weekday + int(max(b.bit_length() for b in font['0'])*scale_date) + 8
draw_text_scaled(buffer,current_time_str,x_time,y_time,width,scale=1.9)

# === Magic Eightball Icon below time ===
eightball_answer = magische_acht_kugel()
icon = eightball_ja_icon if eightball_answer == "Ja" else eightball_no_icon
x_eightball = x_time
y_eightball = y_time + int(max(b.bit_length() for b in font['0']) * scale_date) + 8
draw_icon_inverted(buffer, icon, x_eightball, y_eightball, width)

# === Bus departures at bottom ===
bus_scale = 1.0
line_spacing = 20
bottom_start_y = height - 220
left_x = 0

uni_buses = bus_info['leibniz_departures'][:7]
header_text = "Richtung Uni:"
draw_text_scaled(buffer, header_text, left_x, bottom_start_y, width, scale=bus_scale)

for py_offset in range(3):
    for px in range(left_x, left_x+165):
        py = bottom_start_y + 20 + py_offset
        index = int((px + py*width)//4)
        shift = int((3 - (px % 4))*2)
        buffer[index] &= ~(0x03 << shift)

bus_y_start = bottom_start_y + 38
for i,b in enumerate(uni_buses):
    arrival = b.get('arrival_uni','')
    delay_str = format_delay(b.get('delay',''))
    line_name = clean_bus_line(b['line'])
    if line_name != "X60":
        if line_name == "6":
            line_name = "    6"
        else:
            line_name = "  " + line_name
    line_parts = [line_name, b['departure']]
    if delay_str:
        line_parts.append(delay_str)
    elif arrival:
        line_parts.append("          ")
    if arrival:
        line_parts.append(arrival)
    text = " ".join(line_parts)
    draw_text_scaled(buffer,text,left_x,bus_y_start + i*line_spacing,width,scale=bus_scale)

x_right_start = width//2
x_offset = x_right_start
y_bottom = bottom_start_y

x60_header = "Richtung GEOMAR:"
draw_text_scaled(buffer,x60_header,x_offset,y_bottom,width,scale=bus_scale)

for py_offset in range(3):
    for px in range(x_offset, x_offset+240):
        py = y_bottom + 20 + py_offset
        index = int((px + py*width)//4)
        shift = int((3 - (px % 4))*2)
        buffer[index] &= ~(0x03 << shift)

y_bottom_buses = y_bottom + 38
x60_buses = bus_info['x60_departures'][:3]
other_buses = bus_info['other_departures'][:3]

for i,b in enumerate(x60_buses):
    arrival = b.get('arrival_seefisch','')
    delay_str = format_delay(b.get('delay',''))
    line_parts = ['X60', b['departure']]
    if delay_str:
        line_parts.append(delay_str)
    elif arrival:
        line_parts.append("          ")
    if arrival:
        line_parts.append(arrival)
    text = " ".join(line_parts)
    draw_text_scaled(buffer,text,x_offset,y_bottom_buses + i*line_spacing,width,scale=bus_scale)

y_other_start = y_bottom_buses + len(x60_buses)*line_spacing + 16
for i,b in enumerate(other_buses):
    arrival = b.get('arrival','')
    delay_str = format_delay(b.get('delay',''))
    line_name = clean_bus_line(b['line'])
    if line_name != "X60":
        if line_name == "6":
            line_name = "    6"
        else:
            line_name = "  " + line_name
    line_parts = [line_name, b['departure']]
    if delay_str:
        line_parts.append(delay_str)
    elif arrival:
        line_parts.append("          ")
    if arrival:
        line_parts.append(arrival)
    text = " ".join(line_parts)
    draw_text_scaled(buffer,text,x_offset,y_other_start + i*line_spacing,width,scale=bus_scale)

# === Display ===
epd.display_4Gray(buffer)
epd.sleep()
