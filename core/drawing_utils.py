import cv2


def draw_landmarks(frame, landmarks):

    h, w, _ = frame.shape

    # Draw points
    for landmark in landmarks:

        cx = int(landmark.x * w)
        cy = int(landmark.y * h)

        cv2.circle(
            frame,
            (cx, cy),
            4,
            (0, 255, 0),
            -1
        )

    # Skeleton connections
    connections = [

        # Arms
        (11, 13), (13, 15),
        (12, 14), (14, 16),

        # Shoulders
        (11, 12),

        # Torso
        (11, 23), (12, 24),
        (23, 24),

        # Legs
        (23, 25), (25, 27),
        (24, 26), (26, 28)
    ]

    # Draw lines
    for start_idx, end_idx in connections:

        start = landmarks[start_idx]
        end = landmarks[end_idx]

        x1 = int(start.x * w)
        y1 = int(start.y * h)

        x2 = int(end.x * w)
        y2 = int(end.y * h)

        cv2.line(
            frame,
            (x1, y1),
            (x2, y2),
            (255, 0, 0),
            2
        )