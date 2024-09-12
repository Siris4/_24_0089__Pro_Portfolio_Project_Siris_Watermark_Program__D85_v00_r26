import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk, ImageDraw, ImageFont

# ----------- IMAGE WATERMARK SECTION ---------------- #

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
    if grid_mode.get():
        apply_checkered_watermark()
    else:
        if watermark_type.get() == "image":
            update_image_watermark()
        elif watermark_type.get() == "text":
            update_text_watermark()

# ----------- TEXT WATERMARK SECTION ---------------- #

def update_text_watermark():
    """Handles the text watermark, including the font size, color, position, and optional copyright symbol."""
    global base_image_display, img_tk, watermark_pos
    base_image_display = base_image.copy()

    # Get the user input text
    text = watermark_text.get()

    # Apply copyright symbol at the beginning if checked
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
    fill_color = (255, 255, 255, opacity) if text_color.get() == "white" else (0, 0, 0, opacity)

    # Draw the text at the current position
    draw.text(watermark_pos, text, font=font, fill=fill_color)

    # Composite the text image over the base image
    base_image_display = Image.alpha_composite(base_image_display, text_image)

    # Update the display
    img_tk = ImageTk.PhotoImage(base_image_display)
    image_label.config(image=img_tk)
    image_label.image = img_tk
    root.update()

# ----------- IMAGE WATERMARK SECTION ---------------- #

def update_image_watermark():
    """Handles the resizing, positioning, and opacity of image-based watermark."""
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

    # Place watermark at the current position
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

# ----------- CHECKERED GRID MODE SECTION ---------------- #

def apply_checkered_watermark():
    """Apply watermarks in a checkered pattern (alternating between text and image)."""
    global base_image_display, watermark_image, watermark_resized, img_tk, watermark_pos
    base_image_display = base_image.copy()

    # Resize the watermark dynamically based on the slider
    size_percentage = watermark_size_slider.get() / 100.0
    if watermark_image:
        watermark_resized = watermark_image.resize(
            (int(watermark_image.width * size_percentage), int(watermark_image.height * size_percentage)),
            Image.Resampling.LANCZOS
        )

    # Get the user input text and apply copyright symbol if checked
    text = watermark_text.get()
    if include_copyright.get():
        text = f"© {text}"

    # Set up the font and calculate the text dimensions
    font_size = watermark_size_slider.get()
    try:
        font = ImageFont.truetype("arial.ttf", font_size)
    except IOError:
        font = ImageFont.load_default()

    # Create a drawing context
    text_image = Image.new("RGBA", (base_image.width, base_image.height), (255, 255, 255, 0))
    draw = ImageDraw.Draw(text_image)

    # Adjust text opacity
    opacity = int(opacity_slider.get() * 2.55)  # Convert to 0-255 range
    fill_color = (255, 255, 255, opacity) if text_color.get() == "white" else (0, 0, 0, opacity)

    # Get the bounding box of the text to calculate dimensions
    text_bbox = draw.textbbox((0, 0), text, font=font)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]

    # Adjust watermark opacity for image
    if watermark_image:
        watermark_with_opacity = watermark_resized.copy()
        alpha = watermark_with_opacity.split()[3]  # Get the alpha channel
        alpha = alpha.point(lambda p: p * (opacity / 255))  # Apply opacity
        watermark_with_opacity.putalpha(alpha)

    # Checkered pattern - alternate between image and text
    spacing_x = max(text_width, watermark_resized.width) * 2
    spacing_y = max(text_height, watermark_resized.height) * 2

    for row in range(0, base_image.height, spacing_y):
        for col in range(0, base_image.width, spacing_x):
            if (row // spacing_y + col // spacing_x) % 2 == 0:
                # Place image watermark
                if watermark_image:
                    base_image_display.paste(watermark_with_opacity, (col, row), watermark_with_opacity)
            else:
                # Place text watermark
                draw.text((col, row), text, font=font, fill=fill_color)

    # Composite the text image over the base image
    base_image_display = Image.alpha_composite(base_image_display, text_image)

    # Update the display
    img_tk = ImageTk.PhotoImage(base_image_display)
    image_label.config(image=img_tk)
    image_label.image = img_tk
    root.update()

# ----------- SAVE FUNCTION ---------------- #

def save_image():
    """Save the final image with the watermark."""
    file_path = filedialog.asksaveasfilename(
        defaultextension=".png",
        filetypes=[("PNG files", "*.png"), ("JPEG files", "*.jpg;*.jpeg"), ("BMP files", "*.bmp")]
    )
    if file_path:
        base_image_display.save(file_path)
        print(f"Image saved to {file_path}")

# ----------- SUPPORT FUNCTIONS FOR DRAGGING ---------------- #

def start_drag(event):
    global drag_data
    drag_data["start_x"] = event.x
    drag_data["start_y"] = event.y
    drag_data["start_pos_x"] = watermark_pos[0]
    drag_data["start_pos_y"] = watermark_pos[1]

def on_drag(event):
    global watermark_pos
    delta_x = event.x - drag_data["start_x"]
    delta_y = event.y - drag_data["start_y"]

    # Calculate new watermark position
    new_x = drag_data["start_pos_x"] + delta_x
    new_y = drag_data["start_pos_y"] + delta_y

    # Ensure position stays within image boundaries
    new_x = max(0, min(new_x, base_image.width))
    new_y = max(0, min(new_y, base_image.height))

    watermark_pos = (new_x, new_y)
    apply_watermark()

# ----------- TKINTER SETUP AND USER CONTROLS ---------------- #

# Initialize the tkinter window
root = tk.Tk()
root.title("Watermarker with Checkered Mode")

# Set the window size
root.geometry("800x700")

# Create the top frame for image display and Load button
top_frame = tk.Frame(root, width=800, height=300)
top_frame.pack(side="top", fill="x")

# Create the bottom frame for text and image controls
bottom_frame = tk.Frame(root, width=800, height=400)
bottom_frame.pack(side="top", fill="both", expand=True)

# Create left and right frames inside the bottom frame
left_frame = tk.Frame(bottom_frame, width=400, height=400, padx=10, pady=10)
left_frame.pack(side="left", fill="both", expand=True)

right_frame = tk.Frame(bottom_frame, width=400, height=400, padx=10, pady=10)
right_frame.pack(side="right", fill="both", expand=True)

# Create a vertical separator line between the left and right frames
separator = tk.Canvas(bottom_frame, width=2, height=400, bg="black")
separator.pack(side="left", fill="y")

# ----------- IMAGE DISPLAY AND LOAD BUTTON (Top Section) ---------------- #

# Button to load the image
load_button = tk.Button(top_frame, text="Load Image", command=load_image)
load_button.pack(pady=10)

# Label to display the image
image_label = tk.Label(top_frame)
image_label.pack(pady=10)

# ----------- TEXT FEATURES (Left Side) ---------------- #

# Text input for watermark
watermark_text = tk.StringVar()
text_entry = tk.Entry(left_frame, textvariable=watermark_text, width=40)
text_entry.pack(pady=10)

# Checkbox to include the copyright symbol
include_copyright = tk.BooleanVar()  # Single option for the copyright symbol
copyright_checkbox = tk.Checkbutton(left_frame, text="Include ©", variable=include_copyright, command=apply_watermark)
copyright_checkbox.pack(pady=5)

# Text color options (black or white)
text_color = tk.StringVar(value="black")  # Default to black text
black_text_radio = tk.Radiobutton(left_frame, text="Black Text", variable=text_color, value="black", command=apply_watermark)
black_text_radio.pack(pady=5)
white_text_radio = tk.Radiobutton(left_frame, text="White Text", variable=text_color, value="white", command=apply_watermark)
white_text_radio.pack(pady=5)

# Watermark size slider for text
watermark_size_slider = tk.Scale(left_frame, from_=10, to=200, orient="horizontal", label="Text Watermark Size (%)")
watermark_size_slider.pack(pady=10)
watermark_size_slider.set(100)
watermark_size_slider.bind("<Motion>", lambda event: apply_watermark())

# ----------- IMAGE FEATURES (Right Side) ---------------- #

# Button to load the watermark image
load_watermark_button = tk.Button(right_frame, text="Load Watermark Image", command=load_watermark_image)
load_watermark_button.pack(pady=10)

# Opacity slider
opacity_slider = tk.Scale(right_frame, from_=0, to=100, orient="horizontal", label="Image Opacity")
opacity_slider.pack(pady=10)
opacity_slider.set(100)
opacity_slider.bind("<Motion>", lambda event: apply_watermark())

# Checkbox for checkered grid mode
grid_mode = tk.BooleanVar()  # Variable to track the checkbox state
grid_checkbox = tk.Checkbutton(right_frame, text="Checkered Grid Mode", variable=grid_mode, command=apply_watermark)
grid_checkbox.pack(pady=10)

# Save button to save the watermarked image
save_button = tk.Button(right_frame, text="Save Image", command=save_image)
save_button.pack(pady=20)

# Variables to hold images
base_image = None
base_image_display = None
watermark_image = None
watermark_resized = None
img_tk = None

# Variables to hold drag data and watermark position
drag_data = {"start_x": 0, "start_y": 0, "start_pos_x": 0, "start_pos_y": 0}
watermark_pos = (0, 0)

# Bind dragging events
image_label.bind("<Button-1>", start_drag)
image_label.bind("<B1-Motion>", on_drag)

# Start the main loop
root.mainloop()
