function render() {
    const canvas = document.getElementById("grid");
    const ctx = canvas.getContext("2d");
    define_images();

    ctx.fillStyle = "#3f3f3f";
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    const visibleCells = get_visible_cells();
    for (let i=0; i<visibleCells.length; i++) {
        let coord = coord_to_pos(visibleCells[i], 0);
        ctx.drawImage(sea, coord[0], coord[1]);
    };

    const enemyShips = get_visible_enemy_ships();
    for (let i=0; i<enemyShips.length; i++) {
        let coord = coord_to_pos(enemyShips[i][1], enemyShips[i][2]);
        ctx.drawImage(get_img(enemyShips[i][0]), coord[0], coord[1]);
    };

    const hiddenCells = get_hidden_cells();
    for (let i=0; i<hiddenCells.length; i++) {
        let coord = coord_to_pos(hiddenCells[i], 0);
        ctx.drawImage(fog, coord[0], coord[1]);
    };

    const friendlyShips = get_visible_friendly_ships();
    for (let i=0; i<friendlyShips.length; i++) {
        let coord = coord_to_pos(friendlyShips[i][1], friendlyShips[i][2]);
        ctx.drawImage(get_img(friendlyShips[i][0]), coord[0], coord[1]);
    };

    const damagedCells = get_damaged_squares();
    for (let i=0; i<damagedCells.length; i++) {
        let coord = coord_to_pos(damagedCells[i], 0);
        ctx.drawImage(explosion, coord[0], coord[1]);
    };
};

function define_images() {
    const airCarrier_0 = new Image();
    airCarrier_0.src = "/../../assets/airCarrier-0.png";
    const airCarrier_1 = new Image();
    airCarrier_1.src = "/../../assets/airCarrier-1.png";
    const battleship_0 = new Image();
    battleship_0.src = "/../../assets/battleship-0.png";
    const battleship_1 = new Image();
    battleship_1.src = "/../../assets/battleship-1.png";
    const cruiser_0 = new Image();
    cruiser_0.src = "/../../assets/cruiser-0.png";
    const cruiser_1 = new Image();
    cruiser_1.src = "/../../assets/cruiser-1.png";
    const destroyer_0 = new Image();
    destroyer_0.src = "/../../assets/destroyer-0.png";
    const destroyer_1 = new Image();
    destroyer_1.src = "/../../assets/destroyer-1.png";
    const submarine_0 = new Image();
    submarine_0.src = "/../../assets/submarine-0.png";
    const submarine_1 = new Image();
    submarine_1.src = "/../../assets/submarine-1.png";

    const explosion = new Image();
    explosion.src = "/../../assets/explosion.png";
    const fog = new Image();
    fog.src = "/../../assets/explosion.png";
    const sea = new Image();
    sea.src = "/../../assets/explosion.png";
};

function get_img(filename) {
    switch (filename) {
        case "airCarrier-0.png":
            return airCarrier_0;
        case "airCarrier-1.png":
            return airCarrier_1;
        case "battleship-0.png":
            return battleship_0;
        case "battleship-1.png":
            return battleship_1;
        case "cruiser-0.png":
            return cruiser_0;
        case "cruiser-1.png":
            return cruiser_1;
        case "destroyer-0.png":
            return destroyer_0;
        case "destroyer-1.png":
            return destroyer_1;
        case "submarine-0.png":
            return submarine_0;
        case "submarine-1.png":
            return submarine_1;
        default:
            throw Error();
    };
};

function coords_to_pos(coord, rotation) {
    if (rotation == 0) {
        return [16*coord[0]+1, 16*coord[1]+2];
    } else if (rotation == 1) {
        return [16*coord[0]+1, 16*coord[1]+1];
    } else if (rotation == 2) {
        return [16*coord[0]+2, 16*coord[1]+1];
    } else {
        return [16*coord[0]+2, 16*coord[1]+2];
    };
};