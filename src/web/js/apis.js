function api_connect_to_server() {
    fetch('/api/v1/connect', {
        method: 'POST',
        headers:{}}
    )
    api_debug();
}

function api_disconnect_from_server() {
    fetch('/api/v1/disconnect', {
        method: 'POST',
        headers:{}}
    )
    api_debug();
}

function api_debug() {
    fetch('/api/v1/debug', {
        method: 'POST',
        headers:{}}
    )
}

async function api_create_lobby() {
    try {
        const response = await fetch('/api/v1/create_lobby', {
            method: 'POST',
            headers:{}}
        );

        if (!response.ok) {
            throw new Error('Error when creating lobby');
        }

        const data = await response.json();
        const lobby_uid = data['lobby_uid'];
        return lobby_uid;
    } catch (error) {
        console.error("Error:", error.message);
    }

}