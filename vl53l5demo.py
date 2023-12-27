import pimoroni_i2c
import breakout_vl53l5cx
import time
from picographics import PicoGraphics, DISPLAY_LCD_240X240
from pimoroni import RGBLED

# The VL53L5CX requires a firmware blob to start up.
# Make sure you upload "vl53l5cx_firmware.bin" via Thonny to the root of your filesystem
# You can find it here: https://github.com/ST-mirror/VL53L5CX_ULD_driver/blob/no-fw/lite/en/vl53l5cx_firmware.bin

PINS_BREAKOUT_GARDEN = {"sda": 4, "scl": 5}
PINS_PICO_EXPLORER = {"sda": 20, "scl": 21}


# Sensor startup time is proportional to i2c baudrate
# HOWEVER many sensors may not run at > 400KHz (400000)
i2c = pimoroni_i2c.PimoroniI2C(**PINS_BREAKOUT_GARDEN, baudrate=2_000_000)

# Display setup, check your own following display type, default is LCD 240x240
display = PicoGraphics(display=DISPLAY_LCD_240X240)
display.set_backlight(1.0)
BG = display.create_pen(40, 40, 40)
display.set_pen(BG)

# Sensor setup
print("Starting up sensor...")
t_sta = time.ticks_ms()
sensor = breakout_vl53l5cx.VL53L5CX(i2c)
t_end = time.ticks_ms()
print("Done in {}ms...".format(t_end - t_sta))

# Make sure to set resolution and other settings *before* you start ranging
# 4x4 or 8x8
IS_8X8 = True
if IS_8X8:
    sensor.set_resolution(breakout_vl53l5cx.RESOLUTION_8X8)
    # 1-15 Hz for 8x8
    sensor.set_ranging_frequency_hz(15)
else:
    sensor.set_resolution(breakout_vl53l5cx.RESOLUTION_4X4)
    # 1-60 Hz for 4x4
    sensor.set_ranging_frequency_hz(60)

# Start ranging
sensor.start_ranging()


def update_display_grid_distance(sensor_data):
    # Save the distance RGB grid as 2D matrix
    data_colour = []
    # Set the max distance for the sensor
    sensor_max_distance = 750

    # Append the sensor data according to the sensor matrix size,
    # multidimensional append each row of the matrix.
    # Loop through the sensor touple data and append it to the matrix according to rows and columns
    if IS_8X8:
        for column in range(8):
            data_colour.append([])
            for row in range(8):
                # Get the distance value from the sensor touple
                distance = sensor_data.distance[column * 8 + row]
                # Calculate the distance percentage
                distance_colour = 255 - int((distance / sensor_max_distance) * 255)
                # Append the distance colour to the matrix
                data_colour[column].append(distance_colour)
    else:
        for column in range(4):
            data_colour.append([])
            for row in range(4):
                # Get the distance value from the sensor touple
                distance = sensor_data.distance[column * 4 + row]
                # Calculate the distance percentage
                distance_colour = 255 - int((distance / sensor_max_distance) * 255)
                # Append the distance colour to the matrix
                data_colour[column].append(distance_colour)

    # Divide the screen into according grid into the sensor matrix size
    # Get the screen size
    WIDTH, HEIGHT = display.get_bounds()
    if IS_8X8:
        grid_step_x_init = int(WIDTH / 8)
        grid_step_y_init = int(HEIGHT / 8)
    else:
        grid_step_x_init = int(WIDTH / 4)
        grid_step_y_init = int(HEIGHT / 4)
        grid_size = 4


    grid_step_x = 0
    grid_step_y = 0

    display.clear()

    print("Colour matrix: {}".format(data_colour))
    # Draw the grid from the 2-dimensional matrix array
    for column in range(len(data_colour)):
        for row in range(len(data_colour[column])):
            # Set the grid colour pen
            distance_pen = display.create_pen(data_colour[column][row], 0, 0)
            # Set the grid colour
            display.set_pen(distance_pen)
            # Draw the grid
            display.rectangle(grid_step_x, grid_step_y, grid_step_x_init, grid_step_y_init)
            # Increase the grid step of x
            grid_step_x += grid_step_x_init
        # Increase the grid step of y
        grid_step_y += grid_step_y_init
        # Reset the grid step of x
        grid_step_x = 0

    display.update()


while True:
    display.set_pen(BG)
    display.clear()

    if sensor.data_ready():
        # "data" is a namedtuple (attrtuple technically)
        # it includes average readings as "distance_avg" and "reflectance_avg"
        # plus a full 4x4 or 8x8 set of readings (as a 1d tuple) for both values.
        data = sensor.get_data()
        update_display_grid_distance(data)
        print("{}mm {}% (avg: {}mm {}%)".format(
            data.distance[0],
            data.reflectance[0],
            data.distance_avg,
            data.reflectance_avg))




