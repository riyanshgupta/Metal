

function get_video(url) {
    document.getElementById('cont-'+url).innerHTML = `
        <svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" style="margin: auto; display: block;" width="200px" height="200px" viewBox="0 0 100 100" preserveAspectRatio="xMidYMid">
    <g transform="translate(20 50)">
    <circle cx="0" cy="0" r="6" fill="#456caa">
        <animateTransform attributeName="transform" type="scale" begin="-0.375s" calcMode="spline" keySplines="0.3 0 0.7 1;0.3 0 0.7 1" values="0;1;0" keyTimes="0;0.5;1" dur="1s" repeatCount="indefinite"></animateTransform>
    </circle>
    </g><g transform="translate(40 50)">
    <circle cx="0" cy="0" r="6" fill="#88a2ce">
      <animateTransform attributeName="transform" type="scale" begin="-0.25s" calcMode="spline" keySplines="0.3 0 0.7 1;0.3 0 0.7 1" values="0;1;0" keyTimes="0;0.5;1" dur="1s" repeatCount="indefinite"></animateTransform>
    </circle>
    </g><g transform="translate(60 50)">
    <circle cx="0" cy="0" r="6" fill="#c2d2ee">
        <animateTransform attributeName="transform" type="scale" begin="-0.125s" calcMode="spline" keySplines="0.3 0 0.7 1;0.3 0 0.7 1" values="0;1;0" keyTimes="0;0.5;1" dur="1s" repeatCount="indefinite"></animateTransform>
    </circle>
    </g><g transform="translate(80 50)">
    <circle cx="0" cy="0" r="6" fill="#fefefe">
        <animateTransform attributeName="transform" type="scale" begin="0s" calcMode="spline" keySplines="0.3 0 0.7 1;0.3 0 0.7 1" values="0;1;0" keyTimes="0;0.5;1" dur="1s" repeatCount="indefinite"></animateTransform>
    </circle>
    </g>
    </svg>`
    fetch(url, {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json'
        }
    })
        .then(response => {
            return response.json()
        })
        .then(data => {
            let steps = "";
            for(let i=0; i<data['result']["correct_steps"].length; i++){
                steps += String(data['result']["correct_steps"][i]["order"]) +'. '+data['result']["correct_steps"][i]["text"] + "<br>"
            }
            console.log(steps);
            document.getElementById('cont-'+url).innerHTML = `
            <iframe src="https://www.youtube.com/embed/${data['result']['content']['id']} " title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" allowfullscreen></iframe>
    <div class="block ml-2">
        <h5 class="mb-2 text-lg font-bold tracking-tight text-gray-900 dark:text-white">Steps</h5>
        <p class="font-normal text-gray-700 dark:text-gray-400 left">
        ${steps}
        </p>
    </div>
    </div>`
    })
}