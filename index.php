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
	$hydranten = mysqli_query($db_link, $query)
		or die("Fehler: " . mysqli_error($db_link));
	
	$query = "SELECT * FROM tabKFZ WHERE Stichwort like '".$einsatz['Stichwort']."'";
	$kfz_result = mysqli_query($db_link, $query)
		or die("Fehler: " . mysqli_error($db_link));
	$kfz = mysqli_fetch_array($kfz_result);
	
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
						while($row = mysqli_fetch_array($hydranten)){
							printf("[%s,%s,%s]",$row['Nummer'], $row['lat'], $row['lng']);
							if ($i < mysqli_num_rows($hydranten)){
								echo ",";
							}
							$i++;
						}
					?>]; 
					
					function initMap() {
						var einsatzort = {lat: <?php echo $einsatz['lat']?>, lng: <?php echo $einsatz['lng']?>};
						var map = new google.maps.Map(document.getElementById('karte'), {
							center: einsatzort,
							zoom: 17
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
					
					
					
					/*downloadUrl('http://raspberrypi/hydranten.php', function(data) {
						var xml = data.responseXML;
						var markers = xml.documentElement.getElementsByTagName('marker');
						Array.prototype.forEach.call(markers, function(markerElem) {
							var point = new google.maps.LatLng(
								parseFloat(markerElem.getAttribute('lat')),
								parseFloat(markerElem.getAttribute('lng')));
							}
						};*/
						/*var marker = new google.maps.Marker({
						map: map,
						position: point,
						label: icon.label
						});
						
					}*/
				 </script>
				 
				 <script src="https://maps.googleapis.com/maps/api/js?key=AIzaSyDhg93adqrzNISVzbnw9bfhT7Uoddq7riY&callback=initMap" async defer></script>
			</div>
			<footer>
				<p>Copyright <a href="http://www.ff-appen.de">FF Appen</a></p>
			</footer>
		</div>
	</body> 
</html>
