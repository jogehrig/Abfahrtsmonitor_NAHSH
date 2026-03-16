from waveshare_epd import epd7in5_V2
from layout_1 import layout1_icon   # 800x480 array of 0/1

# ------------------------------------------------------------
# Draw fullscreen bitmap
# ------------------------------------------------------------

def draw_fullscreen_bitmap(buffer, bitmap, width, height):
    """
    Draw a full-screen monochrome bitmap (1 = black pixel, 0 = white pixel).
    Bitmap must be height rows × width columns.
    """
    for y in range(height):
        for x in range(width):

            pixel = bitmap[y][x]    # 1 = black, 0 = white

            if pixel:               # If black pixel
                index = (x + y * width) // 4
                shift = (3 - (x % 4)) * 2
                buffer[index] &= ~(0x03 << shift)


# ------------------------------------------------------------
# Main
# ------------------------------------------------------------

def main():
    epd = epd7in5_V2.EPD()
    epd.init()

    width = epd.width       # should be 800
    height = epd.height     # should be 480

    print(f"EPD size: {width}x{height}")

    # Create buffer filled with white (0xFF)
    buffer_size = (width * height) // 4
    buffer = bytearray([0xFF] * buffer_size)

    # Draw the full-screen bitmap
    draw_fullscreen_bitmap(buffer, layout1_icon, width, height)

    # Display it
    epd.display_4Gray(buffer)
    epd.sleep()

    print("Layout 1 displayed.")


if __name__ == "__main__":
    main()
