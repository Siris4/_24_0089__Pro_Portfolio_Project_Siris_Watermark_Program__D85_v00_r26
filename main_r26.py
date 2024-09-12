import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk, ImageDraw, ImageFont

def load_image():
    file_path = filedialog.askopenfilename(
        filetypes=[("Image files", "*.jpg;*.jpeg;*.png;*.bmp")]
    )
    if file_path:
        global base_image, base_image_display, img_tk
        base_image = Image.open(file_path).convert("RGBA")  # Ensure we use RGBA for transparency
        base_image.thumbnail((400, 400))  # Resizing for display
        base_image_display = base_image.copy()  # Copy for dynamic overlay
        img_tk = ImageTk.PhotoImage(base_image_display)
        image_label.config(image=img_tk)
        image_label.image = img_tk
        root.update()

def load_watermark_image():
    file_path = filedialog.askopenfilename(
        filetypes=[("PNG files", "*.png")]
    )
    if file_path:
        global watermark_image, watermark_resized
        watermark_image = Image.open(file_path).convert("RGBA")  # Load PNG with transparency
        apply_watermark()

def apply_watermark():
    if base_image:
        if watermark_type.get() == "image":
            update_image_watermark()
        elif watermark_type.get() == "text":
            update_text_watermark()

def update_image_watermark():
    global base_image_display, watermark_image, watermark_resized, img_tk, watermark_pos
    base_image_display = base_image.copy()

    # Resize the watermark dynamically based on the slider
    size_percentage = watermark_size_slider.get() / 100.0
    watermark_resized = watermark_image.resize(
        (int(watermark_image.width * size_percentage), int(watermark_image.height * size_percentage)),
        Image.Resampling.LANCZOS
    )

    # Adjust watermark opacity
    opacity = int(opacity_slider.get() * 2.55)  # Convert to 0-255 range
    watermark_with_opacity = watermark_resized.copy()
    alpha = watermark_with_opacity.split()[3]  # Get the alpha channel
    alpha = alpha.point(lambda p: p * (opacity / 255))  # Apply opacity
    watermark_with_opacity.putalpha(alpha)

    if grid_mode.get():
        # Checkered pattern - alternating image watermarks in a grid
        spacing_x = watermark_with_opacity.width * 2  # Set spacing between watermarks
        spacing_y = watermark_with_opacity.height * 2

        for x in range(0, base_image.width, spacing_x):
            for y in range(0, base_image.height, spacing_y):
                # Apply watermark on even (x + y) sum positions to create checkered pattern
                if (x // spacing_x + y // spacing_y) % 2 == 0:
                    base_image_display.paste(watermark_with_opacity, (x, y), watermark_with_opacity)
    else:
        # Single watermark mode - Place one watermark at the current position
        watermark_pos = (
            max(0, min(watermark_pos[0], base_image.width - watermark_with_opacity.width)),
            max(0, min(watermark_pos[1], base_image.height - watermark_with_opacity.height))
        )
        base_image_display.paste(watermark_with_opacity, watermark_pos, watermark_with_opacity)

    # Update the display
    img_tk = ImageTk.PhotoImage(base_image_display)
    image_label.config(image=img_tk)
    image_label.image = img_tk
    root.update()

def update_text_watermark():
    global base_image_display, img_tk, watermark_pos
    base_image_display = base_image.copy()

    # Get the user input text
    text = watermark_text.get()

    # Prepend the copyright symbol if the checkbox is selected
    if include_copyright.get():
        text = f"© {text}"

    # Create a blank transparent image to draw the text onto
    text_image = Image.new("RGBA", (base_image.width, base_image.height), (255, 255, 255, 0))

    # Select font size
    font_size = watermark_size_slider.get()

    # Set up a font (You can change the font path to any .ttf file you have)
    try:
        font = ImageFont.truetype("arial.ttf", font_size)
    except IOError:
        font = ImageFont.load_default()  # Fallback to default if font is not found

    # Create a drawing context
    draw = ImageDraw.Draw(text_image)

    # Adjust text opacity
    opacity = int(opacity_slider.get() * 2.55)  # Convert to 0-255 range

    # Text color with applied opacity
    fill_color = (255, 255, 255, opacity) if white_text.get() else (0, 0, 0, opacity)

    # Get the bounding box of the text to calculate dimensions
    text_bbox = draw.textbbox((0, 0), text, font=font)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]

    if grid_mode.get():
        # Checkered pattern - alternating text watermarks in a grid
        spacing_x = text_width * 2  # Set spacing between watermarks
        spacing_y = text_height * 2

        for x in range(0, base_image.width, spacing_x):
            for y in range(0, base_image.height, spacing_y):
                # Apply text on odd (x + y) sum positions to create checkered pattern
                if (x // spacing_x + y // spacing_y) % 2 != 0:
                    draw.text((x, y), text, font=font, fill=fill_color)
    else:
        # Single watermark mode - Place text at the current position
        draw.text(watermark_pos, text, font=font, fill=fill_color)

    # Composite the text image over the base image
    base_image_display = Image.alpha_composite(base_image_display, text_image)

    # Update the display
    img_tk = ImageTk.PhotoImage(base_image_display)
    image_label.config(image=img_tk)
    image_label.image = img_tk
    root.update()

def save_image():
    """Save the final image with the watermark."""
    file_path = filedialog.asksaveasfilename(
        defaultextension=".png",
        filetypes=[("PNG files", "*.png"), ("JPEG files", "*.jpg;*.jpeg"), ("BMP files", "*.bmp")]
    )
    if file_path:
        base_image_display.save(file_path)
        print(f"Image saved to {file_path}")

def start_drag(event):
    # When mouse is clicked, start drag
    global drag_data
    drag_data["start_x"] = event.x
    drag_data["start_y"] = event.y
    drag_data["start_pos_x"] = watermark_pos[0]
    drag_data["start_pos_y"] = watermark_pos[1]

def on_drag(event):
    # When the mouse is moved with button held down, calculate position offset
    global watermark_pos
    delta_x = event.x - drag_data["start_x"]
    delta_y = event.y - drag_data["start_y"]

    # Calculate new watermark position relative to the mouse drag
    new_x = drag_data["start_pos_x"] + delta_x
    new_y = drag_data["start_pos_y"] + delta_y

    # Ensure the new position stays within the image boundaries
    new_x = max(0, min(new_x, base_image.width))
    new_y = max(0, min(new_y, base_image.height))

    # Update the watermark position and refresh the image
    watermark_pos = (new_x, new_y)
    apply_watermark()

def add_placeholder(event):
    """Adds placeholder text when the entry is empty."""
    if watermark_text.get() == "":
        watermark_entry.config(fg="grey")
        watermark_text.set("Enter text here, if using text watermark")

def remove_placeholder(event):
    """Removes placeholder text when the user clicks on the entry."""
    if watermark_text.get() == "Enter text here, if using text watermark":
        watermark_entry.config(fg="black")
        watermark_text.set("")

# Initialize the tkinter window
root = tk.Tk()
root.title("Siris Watermarker")

# Set the initial size of the window (width x height)
root.geometry("600x800")

# Label to display the image
image_label = tk.Label(root)
image_label.pack()

# Button to load the image
load_button = tk.Button(root, text="Load Image", command=load_image)
load_button.pack(pady=5)

# Frame to hold the text entry, copyright checkbox, and white text checkbox
text_frame = tk.Frame(root)
text_frame.pack(pady=5)

# Checkbox to include the copyright symbol (left side of the text box)
include_copyright = tk.BooleanVar()
copyright_checkbox = tk.Checkbutton(text_frame, text="Include ©", variable=include_copyright, command=apply_watermark)
copyright_checkbox.pack(side="left", padx=5)

# Text input for watermark with placeholder (center of the frame)
watermark_text = tk.StringVar()
watermark_entry = tk.Entry(text_frame, textvariable=watermark_text, width=40)
watermark_entry.pack(side="left", padx=5)

# Set the placeholder initially
watermark_text.set("Enter text here, if using text watermark")
watermark_entry.config(fg="grey")

# Bind focus events for placeholder text
watermark_entry.bind("<FocusIn>", remove_placeholder)
watermark_entry.bind("<FocusOut>", add_placeholder)

# Checkbox to toggle white text (right side of the text box)
white_text = tk.BooleanVar()  # Variable to track the white text checkbox
white_text_checkbox = tk.Checkbutton(text_frame, text="White Text", variable=white_text, command=apply_watermark)
white_text_checkbox.pack(side="left", padx=5)

# Radiobutton to choose text watermark
watermark_type = tk.StringVar(value="image")  # Default to image watermark
text_radio = tk.Radiobutton(root, text="Text Watermark", variable=watermark_type, value="text", command=apply_watermark)
text_radio.pack(pady=5)

# Frame to hold the Opacity and Size sliders
slider_frame = tk.Frame(root)
slider_frame.pack(pady=5)

# Opacity slider (left side)
opacity_slider = tk.Scale(slider_frame, from_=0, to=100, orient="horizontal", label="Opacity")
opacity_slider.pack(side="left", padx=5)
opacity_slider.set(100)  # Set default opacity to 100%
opacity_slider.bind("<Motion>", lambda event: apply_watermark())

# Watermark size slider (right side)
watermark_size_slider = tk.Scale(slider_frame, from_=10, to=200, orient="horizontal", label="Watermark Size (%)")
watermark_size_slider.pack(side="left", padx=5)
watermark_size_slider.set(100)  # Default size is 100%
watermark_size_slider.bind("<Motion>", lambda event: apply_watermark())

# Radiobutton to choose image watermark
image_radio = tk.Radiobutton(root, text="Image Watermark", variable=watermark_type, value="image", command=apply_watermark)
image_radio.pack(pady=5)

# Button to load the watermark image (moved directly under the image watermark radio button)
load_watermark_button = tk.Button(root, text="Load Watermark Image", command=load_watermark_image)
load_watermark_button.pack(pady=5)

# Checkbox for grid mode
grid_mode = tk.BooleanVar()  # Variable to track the checkbox state
grid_checkbox = tk.Checkbutton(root, text="Multiple Tile Grid Mode", variable=grid_mode, command=apply_watermark)
grid_checkbox.pack(pady=5)

# Button to save the image
save_button = tk.Button(root, text="Save Image", command=save_image)
save_button.pack(pady=5)

# Variables to hold images
base_image = None
base_image_display = None
watermark_image = None
watermark_resized = None
img_tk = None

# Variables to hold drag data and watermark position
drag_data = {"start_x": 0, "start_y": 0, "start_pos_x": 0, "start_pos_y": 0}
watermark_pos = (0, 0)  # Initial watermark position at the top-left corner

# Binding the dragging events to the image label
image_label.bind("<Button-1>", start_drag)
image_label.bind("<B1-Motion>", on_drag)

# Start the main loop
root.mainloop()
