import cv2
import face_recognition
import os
import pickle

dataset_path = "dataset"
known_encodings = []
known_roll_nos = []

print("⏳ Started encoding faces from the dataset...")

# Loop through every image file inside the 'dataset' folder
for file_name in os.listdir(dataset_path):
    # Only process image files
    if not file_name.endswith(('.jpg', '.jpeg', '.png')):
        continue
        
    # Extract the Roll No. 
    # E.g., "101_1.jpg" splits into ["101", "1.jpg"], we take the first part.
    roll_no = file_name.split("_")[0]
    image_path = os.path.join(dataset_path, file_name)

    # Load and convert the image to RGB
    image = cv2.imread(image_path)
    rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    # Find the face and turn it into a mathematical encoding
    encodings = face_recognition.face_encodings(rgb_image)

    if len(encodings) > 0:
        known_encodings.append(encodings[0])
        known_roll_nos.append(roll_no)
        print(f"✅ Encoded: {file_name} (Roll No: {roll_no})")
    else:
        print(f"❌ No face found in: {file_name}")

# Save the data so our main attendance script can use it later
print("\n💾 Saving encodings to file...")
data = {"encodings": known_encodings, "roll_nos": known_roll_nos}

with open("encodings.pickle", "wb") as f:
    pickle.dump(data, f)

print("🎉 All done! Encodings saved to 'encodings.pickle'")