<?php include 'db.php'; ?>
<!DOCTYPE html>
<html>
<head><title>Parcels</title></head>
<body>
<h2>Parcel List</h2>
<table border="1">
  <tr>
    <th>ID</th>
    <th>Recipient</th>
    <th>Tracking</th>
    <th>Status</th>
    <th>Date</th>
  </tr>
<?php
$result = $conn->query("SELECT * FROM parcels");
while($row = $result->fetch_assoc()) {
  echo "<tr>
    <td>{$row['id']}</td>
    <td>{$row['recipient_name']}</td>
    <td>{$row['tracking_number']}</td>
    <td>{$row['status']}</td>
    <td>{$row['received_date']}</td>
  </tr>";
}
?>
</table>
</body>
</html>
