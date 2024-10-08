<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Index</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background-color: #f4f4f4;
            margin: 0;
            padding: 0;
            display: flex;
            justify-content: center;
            align-items: center;
            /* height: 100vh; */
        }
        .container {
            background-color: #fff;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
            text-align: center;
        }
        .container h1 {
            margin-bottom: 20px;
        }
        .container form {
            margin-bottom: 20px;
        }
        .container input[type="file"] {
            margin-bottom: 20px;
        }
        .container button {
            padding: 10px 20px;
            width: 100%;
            background-color: #1900ff;
            color: #fff;
            border: none;
            border-radius: 4px;
            cursor: pointer;
        }
        .container button:hover {
            background-color: #008cff;
        }
        .container #data-container {
            margin-top: 20px;
        }
    </style>
    <link rel="icon" href="/favicon.ico" type="image/x-icon">
</head>
<body>
    <div class="container">
        <h1>Upload Your File</h1>
        <form action="/upload" method="post" enctype="multipart/form-data">
            <input type="file" name="file_1" id="file" accept=".jpg, .jpeg, .png" required>
            <input type="text" name="key_1" id="key" placeholder="Application id" required>
            <button type="submit">Upload</button>
        </form>
        <div id="data-container"></div>
    </div>
    <div class="container">
        <h1>Back Page File</h1>
        <form action="/upload_back" method="post" enctype="multipart/form-data">
            <input type="file" name="file_2" id="file-back" accept=".jpg, .jpeg, .png" >
            <input type="text" name="key_2" id="key-back" placeholder="Application id" >
            <button type="submit">Upload Back</button>
        </form>
        <div id="data-container-back"></div>
    </div>
</body>
</html>
