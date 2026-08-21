# AI Personal Trainer: Biomechanical Analysis of Exercise Forms

A computer vision-based desktop application that analyzes exercise movements in real time and provides users with immediate feedback on their exercise form.

## Overview

**AI Personal Trainer: Biomechanical Analysis of Exercise Forms** is a Final Year Project developed as part of the BS Computer Science program at the University of Central Punjab.

The project aims to make basic exercise guidance more accessible by using a standard webcam instead of wearable sensors or specialized motion-capture equipment. The application detects human body landmarks, calculates relevant joint angles, analyzes exercise movements, counts repetitions, and provides real-time visual and audio feedback.

The current implementation supports:

* Squats
* Bicep Curls
* Crunches

Each supported exercise has its own analysis logic for evaluating movement and exercise form.

## Key Features

* Real-time human pose estimation
* Markerless exercise analysis using a standard webcam
* Joint-angle calculation
* Exercise-specific biomechanical analysis
* Automatic repetition counting
* Real-time visual feedback
* Audio feedback
* User calibration before exercise sessions
* Workout performance summary
* Modular exercise-analysis architecture
* Windows executable deployment using PyInstaller

## System Architecture

The application follows a modular architecture consisting broadly of:

```text
User Interface
      │
      ▼
Exercise Screens
      │
      ▼
Pose Detection
      │
      ▼
Landmark & Joint-Angle Analysis
      │
      ▼
Exercise Analyzer
      │
      ├── Squat Analyzer
      ├── Bicep Curl Analyzer
      └── Crunch Analyzer
      │
      ▼
Feedback
      │
      ├── Visual Feedback
      └── Audio Feedback
      │
      ▼
Workout Summary
```

## Technologies Used

| Technology                | Purpose                                           |
| ------------------------- | ------------------------------------------------- |
| Python                    | Core application development                      |
| MediaPipe Pose Landmarker | Human pose estimation                             |
| OpenCV                    | Webcam capture and computer vision operations     |
| NumPy                     | Numerical and mathematical calculations           |
| PyInstaller               | Packaging the application as a Windows executable |

## Project Structure

```text
AI-Personal-Trainer/
│
├── assets/             # Application images and other resources
├── models/             # Pose estimation model files
├── core/               # Core processing components
├── exercises/          # Exercise-specific screens and analyzers
├── ui/                 # User interface components
├── utils/              # Camera utilities
├── main.py             # Application entry point
├── requirements.txt    # Python dependencies
└── README.md
```

## Getting Started

### Prerequisites

For running the application from source, the following are required:

* Windows 10/11
* Python 3.12 or compatible Python version
* A functioning webcam

### Installation

Clone the repository:

```bash
git clone https://github.com/Dr-Mystic/AI-Personal-Trainer.git
cd AI-Personal-Trainer
```

Create and activate a virtual environment:

```bash
python -m venv .venv
```

Windows PowerShell:

```bash
.venv\Scripts\Activate.ps1
```

Install the required dependencies:

```bash
pip install -r requirements.txt
```

### Running from Source

```bash
python main.py
```

### Running the Executable

A Windows executable can be generated using PyInstaller. Once built, launch the generated executable from the `dist` directory.

## Using the Application

1. Launch the application.
2. Complete the calibration process.
3. Select the desired exercise.
4. Position yourself so that your body is clearly visible to the webcam.
5. Perform the selected exercise.
6. Follow the visual and audio feedback provided by the system.
7. Complete the workout and review the generated summary.

For reliable pose detection, users should ensure adequate lighting and keep the relevant body parts visible within the camera frame.

## Current Exercise Support

### Squats

The squat analyzer evaluates lower-body movement using relevant hip, knee, and ankle landmarks. It performs repetition counting and evaluates movement characteristics such as joint angles and body symmetry.

### Bicep Curls

The bicep curl analyzer evaluates arm movement using relevant upper-body landmarks and tracks repetitions for the left and right sides.

### Crunches

The crunch analyzer evaluates upper-body movement using relevant body landmarks and uses movement thresholds to identify repetitions.

## Limitations

The current implementation is a prototype developed for academic and research purposes. Its accuracy can be affected by factors such as:

* Camera position
* Lighting conditions
* Occlusion of body landmarks
* Clothing and background
* Distance from the camera
* Individual differences in movement patterns

The application should not be considered a replacement for a qualified medical professional, physiotherapist, or certified fitness trainer.

## Future Work

Potential future improvements include:

* Support for additional exercises
* More advanced personalized biomechanical profiling
* Expanded exercise-quality metrics
* Physiotherapist/trainer dashboards
* User accounts and long-term progress tracking
* Integration with fitness equipment and wearable devices
* Mobile platform support
* More advanced machine-learning-based movement classification
* Cloud-based workout history and analytics

## Academic Project

**Project Title:**
AI Personal Trainer: Biomechanical Analysis of Exercise Forms

**Degree:**
BS Computer Science

**Institution:**
University of Central Punjab

**Project Type:**
Final Year Project

**Defense:**
30 July 2026

## Contributors

* **Muhammad Farooq Nawaz Khan**
* **Muhammad Ali Nawaz**
* **Ahmad Waheed**

Project development was carried out collaboratively with project teammates, including separate development work that was later integrated into the final application.

## Disclaimer

This software is an academic project and is provided for educational and research purposes. Exercise feedback generated by the application should not be treated as medical advice or as a substitute for professional fitness or medical supervision.