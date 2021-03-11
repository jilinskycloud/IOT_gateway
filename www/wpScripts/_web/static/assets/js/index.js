$(function() {
    "use strict";
    // chart 2

		var ctx = document.getElementById("chart2").getContext('2d');
		var t_mem = document.getElementById('t_mem').innerText;
		var u_mem = document.getElementById('u_mem').innerText;
		var a_mem = document.getElementById('a_mem').innerText;
			var myChart = new Chart(ctx, {
				type: 'doughnut',
				data: {
					labels: ["Total", "Used", "Available"],//, "Other"],
					datasets: [{
						backgroundColor: [
							"#ffffff",
							"rgba(255, 255, 255, 0.70)",
							"rgba(255, 255, 255, 0.50)"
							//"rgba(255, 255, 255, 0.20)"
						],
						data: [t_mem, u_mem, a_mem],//, 1105],
						borderWidth: [0, 0, 0]//, 0]
					}]
				},
			options: {
				maintainAspectRatio: false,
			   legend: {
				 position :"bottom",	
				 display: false,
				    labels: {
					  fontColor: '#ddd',  
					  boxWidth:15
				   }
				}
				,
				tooltips: {
				  displayColors:false
				}
			   }
			});
		

		
		
   });	 
   