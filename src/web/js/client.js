let client_turn_interval = null;
let wait_for_opponent_interval = null;

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
                poll_while_client_turn();
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