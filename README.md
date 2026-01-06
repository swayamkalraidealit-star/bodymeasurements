# Body Measurement from Photos

A computer vision-powered web application that extracts precise anthropometric measurements from full-body photographs using MediaPipe pose estimation.

## Features

- 📸 **Dual Image Analysis**: Upload front and side view photos for comprehensive measurements
- 📏 **Multiple Measurements**: Shoulder width, chest, waist, hip, height, and inseam
- 🎯 **High Accuracy**: MediaPipe's 33-point pose detection with calibration
- 🎨 **Premium UI**: Modern dark mode design with glassmorphism effects
- 📊 **Visual Feedback**: Skeleton overlay to verify pose detection
- 💾 **Export Results**: Download measurements as JSON

## Requirements

- Python 3.8+
- Webcam or smartphone camera (for taking photos)
- Good lighting conditions for best results

## Installation

1. **Clone or navigate to the project directory**:
   ```bash
   cd /home/ideal39/Desktop/body
   ```

2. **Create and activate virtual environment**:
   ```bash
   python3 -m venv env
   source env/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Create environment file**:
   ```bash
   cp .env.example .env
   ```

## Usage

1. **Start the server**:
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

2. **Open your browser**:
   Navigate to `http://localhost:8000`

3. **Upload images**:
   - **Front view**: Stand straight facing the camera, arms slightly away from body
   - **Side view**: Stand in profile, arms at sides
   - Ensure good lighting and wear fitted clothing

4. **Enter calibration height**:
   Input your actual height for accurate measurements

5. **View results**:
   See all measurements displayed with visual gauges

## Photo Guidelines

For best accuracy:
- ✅ Wear fitted clothing
- ✅ Stand 2-3 meters from camera
- ✅ Good, even lighting
- ✅ Plain background
- ✅ Full body visible (head to feet)
- ✅ Natural standing posture

Avoid:
- ❌ Baggy/loose clothing
- ❌ Accessories that obscure body
- ❌ Poor lighting or shadows
- ❌ Cluttered backgrounds
- ❌ Partial body photos

## API Endpoints

- `GET /` - Web interface
- `POST /api/measurements/calculate` - Process images and return measurements
- `GET /api/measurements/health` - Health check

## Measurement Descriptions

- **Shoulder Width**: Distance between shoulder joints
- **Chest**: Circumference at fullest part (requires side view)
- **Waist**: Circumference at natural waistline
- **Hip**: Circumference at widest point
- **Height**: Total body height
- **Inseam**: Inside leg length (hip to ankle)

## Troubleshooting

**Issue**: Pose not detected
- Ensure entire body is visible in frame
- Improve lighting conditions
- Try a plain background

**Issue**: Inaccurate measurements
- Verify calibration height is correct
- Ensure photos are taken from appropriate distance
- Wear more fitted clothing

**Issue**: Server won't start
- Check if port 8000 is available
- Verify all dependencies are installed
- Check Python version (3.8+)

## Technical Details

- **Frontend**: HTML, CSS, Vanilla JavaScript
- **Backend**: FastAPI, Python
- **Computer Vision**: MediaPipe Pose
- **Image Processing**: OpenCV, Pillow

## License

MIT License
