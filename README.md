# Pose Detection – Neckline

![tests](https://github.com/KTVshwajith/Pose-Detection-Neckline/actions/workflows/tests.yml/badge.svg)
![Python](https://img.shields.io/badge/Python-3.9–3.12-3776AB?logo=python&logoColor=white)
![MediaPipe](https://img.shields.io/badge/MediaPipe-Pose-0097A7)
![OpenCV](https://img.shields.io/badge/OpenCV-4-5C3EE8?logo=opencv&logoColor=white)

Measures **neck and torso inclination** from an ordinary video or webcam to flag poor posture during manual lifting. It is part of my research on vision-based detection of posture errors that lead to musculoskeletal disorders, published in *Smart and Sustainable Built Environment* ([doi:10.1108/SASBE-02-2023-0037](https://doi.org/10.1108/SASBE-02-2023-0037)).

▶ **Try it in your browser:** the same method runs live in the pose demo on my [portfolio](https://ktvshwajith.github.io/portfolio-KasunM/#pose).

## How it works

1. **MediaPipe Pose** detects 33 body landmarks in each frame.
2. The script takes the **shoulder, ear and hip** on the side facing the camera.
3. Two angles are measured against a vertical reference line:
   - **Neck inclination:** shoulder → ear
   - **Torso inclination:** hip → shoulder

   `θ = acos( (y₂ − y₁)(−y₁) / (‖p₂ − p₁‖ · y₁) )`
4. Frames where the neck exceeds 40° or the torso exceeds 20° are flagged and drawn in red.

```
        ear ●
             \   ← neck inclination
   ┆          \
   ┆  shoulder ●
   ┆          /
   ┆         /   ← torso inclination
   ┆  hip   ●
 vertical reference
```

## Run it

```bash
pip install -r requirements.txt

python posture_neckline.py --source Resources/lifting_02.mp4   # a video file
python posture_neckline.py --source 0                          # webcam
python posture_neckline.py --source clip.mp4 --save out.mp4 --no-display
```

Output: an annotated preview (press **q** to quit), plus a summary of how many frames were flagged.

## Files

| File | What it is |
|---|---|
| `posture_neckline.py` | Command-line script: video or webcam in, annotated video and posture summary out |
| `test_geometry.py` | Unit tests for the angle calculations (run with `pytest`) |
| `Pose Detection-Neckline- Uploading-v0.1.ipynb` | Original research notebook |

## Notes

- The script fixes two small issues from the notebook: the degree conversion used `int(180/π)` (57 instead of 57.296, under-reporting angles by about 0.5%), and a variable was overwritten when reading the right shoulder.
- It uses whichever side of the body is more visible, so the camera can be on the person's left or right.
- The 40° and 20° limits are illustrative; set `NECK_LIMIT` and `TORSO_LIMIT` for your own study.

## Author

**Dr Kasun Moolikagedara**, PhD (AUT) · [Portfolio](https://ktvshwajith.github.io/portfolio-KasunM/) · [LinkedIn](https://www.linkedin.com/in/kasun-mg) · [Google Scholar](https://scholar.google.com/citations?user=w_nMxr8AAAAJ&hl=en)
