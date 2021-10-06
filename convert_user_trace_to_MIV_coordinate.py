import pandas as pd

df = pd.read_csv("pose.csv")
df['y'] = -df['y']
df['z'] = -df['z']
df['yaw'] = -df['yaw']
df['pitch'] = -df['pitch']
df = df.drop(columns=['t', 'valid'])

new_df = pd.DataFrame(data={'X': df['x'].values, 'Y': df['y'].values, 'Z': df['z'].values,
                            'Yaw': df['yaw'].values, 'Pitch': df['pitch'].values, 'Roll': df['roll'].values})
new_df.to_csv("converted_pose.csv", index=False)
