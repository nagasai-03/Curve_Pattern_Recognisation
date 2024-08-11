import os
from flask import Flask, render_template, request, send_from_directory, redirect, url_for
import numpy as np
import matplotlib.pyplot as plt

app = Flask(__name__)

# Configuration for upload and processed directories
app.config['UPLOAD_PATH'] = os.path.join('static', 'uploaded_files')
app.config['PROCESSED_PATH'] = os.path.join('static', 'processed_files')

# Create directories if they don't exist
os.makedirs(app.config['UPLOAD_PATH'], exist_ok=True)
os.makedirs(app.config['PROCESSED_PATH'], exist_ok=True)

# Function to load CSV data and return a structured path list
def load_csv_data(csv_file_path):
    data = np.genfromtxt(csv_file_path, delimiter=',')
    path_data = []

    for path_id in np.unique(data[:, 0]):
        path_points = data[data[:, 0] == path_id][:, 1:]
        segments = []

        for segment_id in np.unique(path_points[:, 0]):
            segment = path_points[path_points[:, 0] == segment_id][:, 1:]
            segments.append(segment)

        path_data.append(segments)

    return path_data

# Placeholder function for different curve processing types
def handle_curve_processing(path_data, process_option):
    if process_option == "symmetry":
        return apply_symmetry(path_data)
    elif process_option == "regularize":
        return regularize_path(path_data)
    elif process_option == "complete":
        return complete_paths(path_data)
    else:
        return path_data

def apply_symmetry(path_data):
    # Example symmetry logic: flipping over the y-axis
    symmetrical_paths = []
    for path in path_data:
        symmetrical_segments = []
        for segment in path:
            flipped_segment = np.copy(segment)
            flipped_segment[:, 0] = -flipped_segment[:, 0]  # Flip over y-axis
            symmetrical_segments.append(flipped_segment)
        symmetrical_paths.append(symmetrical_segments)
    return symmetrical_paths

def regularize_path(path_data):
    # Placeholder for regularization logic
    return path_data

def complete_paths(path_data):
    # Placeholder for curve completion logic
    return path_data

# Function to save processed path data to a CSV file
def save_to_csv(path_data, output_file_path):
    rows = []
    for path_idx, path in enumerate(path_data):
        for segment_idx, segment in enumerate(path):
            for point_idx, point in enumerate(segment):
                rows.append([path_idx, segment_idx, point_idx, point[0], point[1]])

    np.savetxt(output_file_path, rows, delimiter=',', fmt='%d,%d,%d,%f,%f')

# Function to plot the processed curves and save as an image
def generate_plot(path_data, output_image_name):
    plt.figure(figsize=(10, 10))
    for path in path_data:
        for segment in path:
            plt.plot(segment[:, 0], segment[:, 1], 'b-', linewidth=2)  # 'b-' is for blue color
    
    image_path = os.path.join(app.config['PROCESSED_PATH'], f'{output_image_name}.png')
    plt.savefig(image_path)
    plt.close()
    return image_path

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        if 'file' not in request.files:
            return 'No file selected'
        uploaded_file = request.files['file']
        if uploaded_file.filename == '':
            return 'No file chosen'
        if uploaded_file:
            saved_file_name = uploaded_file.filename
            saved_file_path = os.path.join(app.config['UPLOAD_PATH'], saved_file_name)
            uploaded_file.save(saved_file_path)

            # Load and process the uploaded file
            path_data = load_csv_data(saved_file_path)

            # Process the curves based on the selected option
            process_option = request.form['process_type']
            processed_data = handle_curve_processing(path_data, process_option)

            # Save the processed data to a CSV file
            output_csv_name = f"{os.path.splitext(saved_file_name)[0]}_processed.csv"
            output_csv_path = os.path.join(app.config['PROCESSED_PATH'], output_csv_name)
            save_to_csv(processed_data, output_csv_path)

            # Generate the output image based on processing type
            if process_option == "symmetry":
                image_name = f"{os.path.splitext(saved_file_name)[0]}_symmetry"
            else:
                image_name = f"{os.path.splitext(saved_file_name)[0]}_processed"
                
            # Plot and save the processed curves as an image
            processed_image_path = generate_plot(processed_data, image_name)

            # Redirect to avoid form resubmission
            return redirect(url_for('home', processed_file=output_csv_name, plot_image=os.path.basename(processed_image_path)))

    return render_template('index.html', processed_file=request.args.get('processed_file'), plot_image=request.args.get('plot_image'))

@app.route('/download_file/<filename>')
def download_file(filename):
    return send_from_directory(app.config['PROCESSED_PATH'], filename)

@app.route('/download_image/<filename>')
def download_image(filename):
    return send_from_directory(app.config['PROCESSED_PATH'], filename)

if __name__ == '__main__':
    app.run(debug=True)