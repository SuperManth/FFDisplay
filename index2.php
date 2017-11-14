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
	
	$query = "SELECT * FROM tabHydranten WHERE lat < (".$einsatz['lat']." + 0.001000) AND lat > (".$einsatz['lat']."-0.001000) AND lng > (".$einsatz['lng']."-0.001000) AND lng < (".$einsatz['lng']."+0.001000)";
	$result = mysqli_query($db_link, $query)
		or die("Fehler: " . mysqli_error($db_link));
	
	$query = "SELECT * FROM tabKFZ WHERE Stichwort like '".$einsatz['Stichwort']."'";
	$kfz_result = mysqli_query($db_link, $query)
		or die("Fehler: " . mysqli_error($db_link));
	$kfz = mysqli_fetch_array($kfz_result);
	
	$ff_lat = 53.663151;
	$ff_lng = 9.732960;
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
			<header>
				<p><?php echo $einsatz['Stichwort']?> - <?php echo $kfz['Fahrzeug']?></p>
				<marquee behavior="alternate"><?php echo $einsatz['Datum']?> - <?php echo $einsatz['Alarmierung']?></marquee>
			</header>
			<div id="infotext">
				<H1>EINSATZORT</H1>
				<P><?php echo $einsatz['Name']?></p><br>
				<p><?php echo $einsatz['Strasse']?></p><br>
				<p><?php echo $einsatz['Ort']?></p><br>
				<p><?php echo $einsatz['Adresse2']?></p><br>
				<p><?php echo $einsatz['InfoText']?></p><br>
				<p><?php echo $einsatz['ZusatzInfo']?></p><br>
				<p><?php echo $einsatz['Person']?></p><br>
				<p><?php echo $einsatz['Feld07']?></p><br>
				<p><?php echo $einsatz['Feld10']?></p><br>
				<p><?php echo $einsatz['Feld11']?></p><br>
				<p><?php echo $einsatz['Feld12']?></p><br>
				<p><?php echo $einsatz['Feld13']?></p><br>
				<p><?php echo $einsatz['Feld14']?></p><br>
				<p><?php echo $einsatz['Sonderrechte']?></p><br>
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
							var directionsService = new google.maps.DirectionsService;
							var directionsDisplay = new google.maps.DirectionsRenderer;
							var map = new google.maps.Map(document.getElementById('karte'), {
								zoom: 12,
								center: {lat: <?php echo $ff_lat?>, lng: <?php echo $ff_lng?>}
							});
							directionsDisplay.setMap(map);

							calculateAndDisplayRoute(directionsService, directionsDisplay);
							setMarkers(map2);
						}
	
						function calculateAndDisplayRoute(directionsService, directionsDisplay) {
							directionsService.route({
							origin: {lat: <?php echo $ff_lat?>, lng: <?php echo $ff_lng?>},
							destination: {lat: <?php echo $einsatz['lat']?>, lng: <?php echo $einsatz['lng']?>},
							travelMode: 'DRIVING'
							}, function(response, status) {
								if (status === 'OK') {
									directionsDisplay.setDirections(response);
								} else {
									window.alert('Directions request failed due to ' + status);
								}
							});
						}
					
					function setMarkers(map) {
						for (var i = 0; i <  markers2.length; i++) {
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
