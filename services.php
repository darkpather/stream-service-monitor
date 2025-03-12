<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>FFMPEG Services</title>
    <link rel="stylesheet" href="css/styles.css">
    <script src="js/scripts.js" defer></script>
</head>
<body>
    <div class="container">
        <h1>FFMPEG Service Monitor</h1>
        <table>
            <thead>
                <tr>
                    <th>Service Name</th>
                    <th>Status</th>
                    <th>CPU</th>
                    <th>Memory</th>
                    <th>Codec Name</th>
                    <th>Profile</th>
                    <th>Codec Type</th>
                    <th>Sample Rate</th>
                    <th>Channels</th>
                    <th>Channel Layout</th>
                    <th>Bit Rate</th>
                    <th>Actions</th>
                </tr>
            </thead>
            <tbody id="service-data">
                <!-- Data will be dynamically populated here -->
            </tbody>
        </table>
    </div>
</body>
</html>
