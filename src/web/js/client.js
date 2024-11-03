let client_turn_interval = null;
let wait_for_opponent_interval = null;

let currently_selected_ship = 0;
let choose_fire_square = false;


const airCarrier_0_N = new Image();
airCarrier_0_N.src = "/assets/n-airCarrier-0.png";
const airCarrier_0_S = new Image();
airCarrier_0_S.src = "/assets/s-airCarrier-0.png";
const airCarrier_0_E = new Image();
airCarrier_0_E.src = "/assets/e-airCarrier-0.png";
const airCarrier_0_W = new Image();
airCarrier_0_W.src = "/assets/w-airCarrier-0.png";
const airCarrier_1_N = new Image();
airCarrier_1_N.src = "/assets/n-airCarrier-1.png";
const airCarrier_1_S = new Image();
airCarrier_1_S.src = "/assets/s-airCarrier-1.png";
const airCarrier_1_E = new Image();
airCarrier_1_E.src = "/assets/e-airCarrier-1.png";
const airCarrier_1_W = new Image();
airCarrier_1_W.src = "/assets/w-airCarrier-1.png";
const battleship_0_N = new Image();
battleship_0_N.src = "/assets/n-battleship-0.png";
const battleship_0_S = new Image();
battleship_0_S.src = "/assets/s-battleship-0.png";
const battleship_0_E = new Image();
battleship_0_E.src = "/assets/e-battleship-0.png";
const battleship_0_W = new Image();
battleship_0_W.src = "/assets/w-battleship-0.png";
const battleship_1_N = new Image();
battleship_1_N.src = "/assets/n-battleship-1.png";
const battleship_1_S = new Image();
battleship_1_S.src = "/assets/s-battleship-1.png";
const battleship_1_E = new Image();
battleship_1_E.src = "/assets/e-battleship-1.png";
const battleship_1_W = new Image();
battleship_1_W.src = "/assets/w-battleship-1.png";
const cruiser_0_N = new Image();
cruiser_0_N.src = "/assets/n-cruiser-0.png";
const cruiser_0_S = new Image();
cruiser_0_S.src = "/assets/s-cruiser-0.png";
const cruiser_0_E = new Image();
cruiser_0_E.src = "/assets/e-cruiser-0.png";
const cruiser_0_W = new Image();
cruiser_0_W.src = "/assets/w-cruiser-0.png";
const cruiser_1_N = new Image();
cruiser_1_N.src = "/assets/n-cruiser-1.png";
const cruiser_1_S = new Image();
cruiser_1_S.src = "/assets/s-cruiser-1.png";
const cruiser_1_E = new Image();
cruiser_1_E.src = "/assets/e-cruiser-1.png";
const cruiser_1_W = new Image();
cruiser_1_W.src = "/assets/w-cruiser-1.png";
const destroyer_0_N = new Image();
destroyer_0_N.src = "/assets/n-destroyer-0.png";
const destroyer_0_S = new Image();
destroyer_0_S.src = "/assets/s-destroyer-0.png";
const destroyer_0_E = new Image();
destroyer_0_E.src = "/assets/e-destroyer-0.png";
const destroyer_0_W = new Image();
destroyer_0_W.src = "/assets/w-destroyer-0.png";
const destroyer_1_N = new Image();
destroyer_1_N.src = "/assets/n-destroyer-1.png";
const destroyer_1_S = new Image();
destroyer_1_S.src = "/assets/s-destroyer-1.png";
const destroyer_1_E = new Image();
destroyer_1_E.src = "/assets/e-destroyer-1.png";
const destroyer_1_W = new Image();
destroyer_1_W.src = "/assets/w-destroyer-1.png";
const submarine_0_N = new Image();
submarine_0_N.src = "/assets/n-submarine-0.png";
const submarine_0_S = new Image();
submarine_0_S.src = "/assets/s-submarine-0.png";
const submarine_0_E = new Image();
submarine_0_E.src = "/assets/e-submarine-0.png";
const submarine_0_W = new Image();
submarine_0_W.src = "/assets/w-submarine-0.png";
const submarine_1_N = new Image();
submarine_1_N.src = "/assets/n-submarine-1.png";
const submarine_1_S = new Image();
submarine_1_S.src = "/assets/s-submarine-1.png";
const submarine_1_E = new Image();
submarine_1_E.src = "/assets/e-submarine-1.png";
const submarine_1_W = new Image();
submarine_1_W.src = "/assets/w-submarine-1.png";

const explosion = new Image();
explosion.src = "/assets/explosion.png";
const fog = new Image();
fog.src = "/assets/fog.png";
const sea = new Image();
sea.src = "/assets/sea.png";
const selectedCell = new Image();
selectedCell.src = "/assets/selectedCell.png";

function poll_while_waiting_for_opponent() {
    clearInterval(client_turn_interval);
    if (wait_for_opponent_interval) return;

    wait_for_opponent_interval = setInterval(async () => {
        try {
            let has_finished = await api_has_game_finished();
            if (has_finished) {
                if (await api_is_winner()) {
                    alert("You won");
                } else {
                    alert("You lost");
                }
            }

            let is_my_turn = await api_is_my_turn();
            if (is_my_turn) {
                console.log("It is now the clients turn");
                clearInterval(wait_for_opponent_interval);
                wait_for_opponent_interval = null;
                poll_while_client_turn();
            }
        } catch (error) {
            console.error("Error polling for player status:", error);
        }
    }, 1000)
}

function poll_while_client_turn() {
    clearInterval(wait_for_opponent_interval);
    if (client_turn_interval) return;

    activate_user_input();

    client_turn_interval = setInterval(async () => {
        try {
            let availiable_ships = await api_get_available_ships();
            if (availiable_ships.length <= 0) {
                deactivate_user_input();

                console.log("It is now the clients turn");
                clearInterval(wait_for_opponent_interval);
                wait_for_opponent_interval = null;
                poll_while_waiting_for_opponent();
            }
        } catch (error) {
            console.error("Error polling for player status:", error);
        }
    }, 1000)
}


is_user_input_activated = false;

function activate_user_input() {
    is_user_input_activated = true
}

function deactivate_user_input() {
    is_user_input_activated = false
}

async function render() {
    const canvas = document.getElementById("grid");
    const ctx = canvas.getContext("2d");

    ctx.fillStyle = "#3f3f3f";
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    const visibleCells = await api_get_visible_cells();
    for (let i=0; i<visibleCells.length; i++) {
        let coord = coord_to_pos(visibleCells[i], 0);
        ctx.drawImage(sea, coord[0], coord[1]);
    };

    const enemyShips = await api_get_visible_enemy_ships();
    for (let i=0; i<enemyShips.length; i++) {
        let coord = coord_to_pos(enemyShips[i][1], enemyShips[i][2]);
        ctx.drawImage(get_img(enemyShips[i][0], enemyShips[i][2]), coord[0], coord[1]);
    };
    
    const friendlyShips = await api_get_visible_friendly_ships();
    for (let i=0; i<friendlyShips.length; i++) {
        let coord = coord_to_pos(friendlyShips[i][1], friendlyShips[i][2]);
        ctx.drawImage(get_img(friendlyShips[i][0], friendlyShips[i][2]), coord[0], coord[1]);
    };
    
    const hiddenCells = await api_get_hidden_cells();
    for (let i=0; i<hiddenCells.length; i++) {
        let coord = coord_to_pos(hiddenCells[i], 0);
        ctx.drawImage(fog, coord[0], coord[1]);
    };
    
    const damagedCells = await api_get_damaged_squares();
    for (let i=0; i<damagedCells.length; i++) {
        let coord = coord_to_pos(damagedCells[i], 0);
        ctx.drawImage(explosion, coord[0], coord[1]);
    };
};


function get_img(filename, rotation) {
    if (rotation == 0){
    switch (filename) {
        case "airCarrier-0.png":
            return airCarrier_0_W;
        case "airCarrier-1.png":
            return airCarrier_1_W;
        case "battleship-0.png":
            return battleship_0_W;
        case "battleship-1.png":
            return battleship_1_W;
        case "cruiser-0.png":
            return cruiser_0_W;
        case "cruiser-1.png":
            return cruiser_1_W;
        case "destroyer-0.png":
            return destroyer_0_W;
        case "destroyer-1.png":
            return destroyer_1_W;
        case "submarine-0.png":
            return submarine_0_W;
        case "submarine-1.png":
            return submarine_1_W;
        default:
            throw Error();
    };} else if (rotation == 1)

    {switch (filename) {
        case "airCarrier-0.png":
            return airCarrier_0_N;
        case "airCarrier-1.png":
            return airCarrier_1_N;
        case "battleship-0.png":
            return battleship_0_N;
        case "battleship-1.png":
            return battleship_1_N;
        case "cruiser-0.png":
            return cruiser_0_N;
        case "cruiser-1.png":
            return cruiser_1_N;
        case "destroyer-0.png":
            return destroyer_0_N;
        case "destroyer-1.png":
            return destroyer_1_N;
        case "submarine-0.png":
            return submarine_0_N;
        case "submarine-1.png":
            return submarine_1_N;
        default:
            throw Error();
    };} else if (rotation == 2)

    {switch (filename) {
        case "airCarrier-0.png":
            return airCarrier_0_E;
        case "airCarrier-1.png":
            return airCarrier_1_E;
        case "battleship-0.png":
            return battleship_0_E;
        case "battleship-1.png":
            return battleship_1_E;
        case "cruiser-0.png":
            return cruiser_0_E;
        case "cruiser-1.png":
            return cruiser_1_E;
        case "destroyer-0.png":
            return destroyer_0_E;
        case "destroyer-1.png":
            return destroyer_1_E;
        case "submarine-0.png":
            return submarine_0_E;
        case "submarine-1.png":
            return submarine_1_E;
        default:
            throw Error();
    };} else 

    {switch (filename) {
        case "airCarrier-0.png":
            return airCarrier_0_S;
        case "airCarrier-1.png":
            return airCarrier_1_S;
        case "battleship-0.png":
            return battleship_0_S;
        case "battleship-1.png":
            return battleship_1_S;
        case "cruiser-0.png":
            return cruiser_0_S;
        case "cruiser-1.png":
            return cruiser_1_S;
        case "destroyer-0.png":
            return destroyer_0_S;
        case "destroyer-1.png":
            return destroyer_1_S;
        case "submarine-0.png":
            return submarine_0_S;
        case "submarine-1.png":
            return submarine_1_S;
        default:
            throw Error();
    };}
};

function coord_to_pos(coord, rotation) {
    if (rotation == 0) {
        return [16*coord[0], 16*coord[1]+1];
    } else if (rotation == 1) {
        return [16*coord[0], 16*coord[1]];
    } else if (rotation == 2) {
        return [16*coord[0]+1, 16*coord[1]];
    } else {
        return [16*coord[0]+1, 16*coord[1]+1];
    };
};

function render_fire() {
    const coords = api_get_possible_attacks(currently_selected_ship);
    for (let i=0; i<coords.length; i++) {
        let coord = coord_to_pos(coords[i], 1);
        ctx.drawImage(selectedCell, coord[0], coord[1]);
    };
};

function pos_to_coord(pos){
    return [pos[0] / 16, (pos[1] - 1) / 16]
}


async function on_button_move() {
    if (is_user_input_activated) {
        await api_move(currently_selected_ship, 1);
    }
    render();await switch_current_ship(false);
}

async function on_button_rotate(anti_clockwise) {
    if (is_user_input_activated) {
        await api_rotate(currently_selected_ship, anti_clockwise);
    }
    render();await switch_current_ship(false);
}

async function on_button_fire() {
    if (is_user_input_activated) {
        await render_fire();
        choose_fire_square = true;
    }

    render_fire();


}

//From https://stackoverflow.com/questions/17130395/real-mouse-position-in-canvas
let canv = document.getElementById("grid");
canv.addEventListener('click', event => {
    let bound = canv.getBoundingClientRect();
    let x = event.clientX - bound.left - canv.clientLeft;
    let y = event.clientY - bound.top - canv.clientTop;
    coord = pos_to_coord([x, y]);
    console.log(coord);
    if (choose_fire_square) {
        api_fire(currently_selected_ship, coord);
        choose_fire_square = false;
    }

    render(); switch_current_ship(false);
});

async function switch_current_ship(left) {
    let x = await api_get_available_ships();
    let index = x.indexOf(currently_selected_ship)
    if (left) {
        currently_selected_ship = x[(index - 1) % x.length];
    } else {
        currently_selected_ship = x[(index + 1) % x.length];
    }
    console.log(currently_selected_ship);
    let y = await api_get_ship_details(currently_selected_ship);

    const previewship = document.getElementById("previewship");
    console.log(y);
    previewship.src = ("/assets/e-" + y['filename'])
}

render();

if (api_is_player_one()) {
    poll_while_client_turn();
} else {
    poll_while_waiting_for_opponent();
}
