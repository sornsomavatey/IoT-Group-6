let entryTime = new Date();
document.getElementById("entryTime").innerText = entryTime.toLocaleTimeString();

function toggleMenu() {
    let sidebar = document.getElementById("sidebar");
    let overlay = document.getElementById("overlay");

    if (sidebar.style.left === "0px") {
        sidebar.style.left = "-250px";
        overlay.style.display = "none";
    } else {
        sidebar.style.left = "0px";
        overlay.style.display = "block";
    }
}

function showSection(section) {
    document.querySelectorAll(".section").forEach(s => s.classList.remove("active"));
    document.getElementById(section).classList.add("active");
    toggleMenu();
}

/* Gate Control */
function openGate() { fetch("/open"); }
function closeGate() { fetch("/close"); }

/* Parking Timer */
let seconds = 0;
setInterval(() => {
    seconds++;
    let h = Math.floor(seconds / 3600);
    let m = Math.floor((seconds % 3600) / 60);
    let s = seconds % 60;
    document.getElementById("parkingTimer").innerText =
        `${String(h).padStart(2,'0')}:${String(m).padStart(2,'0')}:${String(s).padStart(2,'0')}`;
}, 1000);

/* Generate Receipt */
function generateReceipt() {
    let exitTime = new Date();
    document.getElementById("exitTime").innerText = exitTime.toLocaleTimeString();

    let durationMinutes = Math.ceil(seconds / 60);
    let hours = Math.ceil(durationMinutes / 60);
    let fee = hours * 1;

    document.getElementById("duration").innerText = `${hours} hour(s)`;
    document.getElementById("totalFee").innerText = fee;
}