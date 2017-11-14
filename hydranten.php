<!DOCTYPE html> 
<?php
	$db_link = mysqli_connect('localhost', 'test', 'test', 'FFDisplay');
	if(!$db_link)
	{
		die("<p>DB Verbindungsfehler</p>");
	}
	$query = "SELECT * FROM tabEinsatz ORDER BY ID DESC LIMIT 1";
	$db_res = mysqli_query($db_link, $query)
		or die("Fehler: " . mysqli_error($db_link));
	$einsatz = mysqli_fetch_array($db_res);
	
	$query = "SELECT * FROM tabHydranten";
	$result = mysqli_query($db_link, $query)
		or die("Fehler: " . mysqli_error($db_link));
	
?> 
<html>
	<head>
		<title>Einsatz Anzeige</title>
		<meta charset=UTF-8"/>
		<meta http-equiv="refresh" content=240; url=<?php echo $_SERVER['PHP_SELF']; ?> />
		<link rel="stylesheet" type="text/css" href="style.css" />
	</head>
	<body>
		<div id="wrapper">
			
			<div id="infotext">
				<H1>Hydranten</H1>
				
			</div>
			<div id="karte">
				<script>
					var map;
					var markers = [
					<?php
						$i=1;
						while($row = mysqli_fetch_array($result)){
							printf("[%s,%s,%s]",$row['Nummer'], $row['lat'], $row['lng']);
							if ($i < mysqli_num_rows($result)){
								echo ",";
							}
							$i++;
						}
					?>]; 
					
					function initMap() {
						var einsatzort = {lat: 53.66315, lng: 9.732960};
						var map = new google.maps.Map(document.getElementById('karte'), {
							center: einsatzort,
							zoom: 16
						});
						var marker = new google.maps.Marker({
							position: einsatzort,
							map: map,
							icon: 'http://maps.google.com/mapfiles/ms/icons/blue-dot.png'
						});
						setMarkers(map);
					}
					
					function setMarkers(map) {
						for (var i = 0; i <  markers.length; i++) {
							var marker = new google.maps.Marker({
								position: {lat: Number(markers[i][1]), lng: Number(markers[i][2])},
								map: map,
								label: 'H'
							});
						};
					}
					
				 </script>
				 
				 <script src="https://maps.googleapis.com/maps/api/js?key=AIzaSyDhg93adqrzNISVzbnw9bfhT7Uoddq7riY&callback=initMap" async defer></script>
			</div>
			<footer>
				<p>Copyright <a href="http://www.ff-appen.de">FF Appen</a></p>
			</footer>
		</div>
	</body> 
</html>
