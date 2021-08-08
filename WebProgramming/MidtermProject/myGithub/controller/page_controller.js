

let btn_obj = document.getElementById('submit_btn')
let msg_obj = document.getElementById('msg')
let myStorage = window.localStorage;


/*
    In this function first, the language scores of the input repo url will be retrieved
    Second, the retrieved information will be saved in a localStorage and then return the
     language score information by accessing the localStorage
 */
async function get_language_score(lang_url) {
    await fetch(lang_url)
        .then(result => {
            return result.json();
        })
        .then(data => {
            let temp_lang = {}
            for (let key in data) {
                if (data.hasOwnProperty(key)) {
                    temp_lang[key] = data[key]
                }
            }
            console.log(temp_lang)
            myStorage.setItem('temp', JSON.stringify(temp_lang))
        })
        .catch(error => {
            msg_obj.style.color = 'red'
            msg_obj.innerHTML = `<p>Error: Network Error, ${error}</p>`
        });
    return myStorage.getItem('temp')
}


/*
    In this function the favorite language of the user will be retrieved based on the last 5 pushed repositories
    First, the list of the user repositories will be retrieved then it will be sorted based on pushed_at value
    Second, the number of lines the user wrote with different languages will be considered as language score and
     retrieved by get_language_score function and then accumulated in temp variable, meanwhile the language that
     has higher lines of code will be updated
    Third, name of the language that has the highest number of lines will be saved in a localStorage and then returned
     by accessing the localStorage
 */
async function favorite_language(repo_link) {
    let repo_info = {}
    let max_key, max_val = 0
    await fetch(repo_link)
        .then(response => {
            return response.json();
        })
        .then(async function (data) {
            data.sort((a, b) => {
                return new Date(b['pushed_at']) - new Date(a['pushed_at']) // descending
            })
            console.log(data)
            let temp = {}
            for (let i = 0; i < Math.min(5, data.length); i++) {
                let score = JSON.parse(await get_language_score(data[i]['languages_url']))
                console.log(score)
                for (let key in score) {
                    if (score.hasOwnProperty(key)) {
                        if (temp.hasOwnProperty(key)) {
                            temp[key] += score[key]
                        }
                        else {
                            temp[key] = score[key]
                        }
                        if (max_val < temp[key]) {
                            max_val = temp[key]
                            max_key = key
                        }
                    }
                }
                myStorage.setItem('favorite_lang', max_key)
            }
        })
        .catch(error => {
            msg_obj.style.color = 'red'
            msg_obj.innerHTML = `<p>Error: Network Error, ${error}</p>`
        });
    console.log(repo_info)
    return myStorage.getItem('favorite_lang')
}


/*
    Update the html page according to the retrieved data
    First, check whether the user was found or not and then if the user was not found then the appropriate message
     will be displayed in the fourth item in the flex container (under the submit button)
     (worth to mention that if the number of request to the api exceeded then the appropriate message will be displayed
      in this part too)
    Second, if the username was found then the elements of the grid container will be updated based on the retrieved
     information of the user and the appropriate message (Information retrieved) will be displayed under the
      submit button
 */
 function update_info(string_data, interested_language) {
    let json_data = JSON.parse(string_data)
    if (json_data['message'] === 'Not Found') {
        msg_obj.style.color = 'red'
        msg_obj.innerHTML = '<p>Error: User Not Found</p>'
    }
    else if (json_data['message'] != null) {
        msg_obj.innerHTML = `<div>Error: ${json_data['message']}</div>`

    }
    else {
        let profile_img_obj = document.getElementById('avatar_img')
        let personal_info_obj= document.getElementById('personal-information')
        let bio_info_obj = document.getElementById('bio_information')
        let personal_info = json_data['name'] ? `<p>${json_data['name']}</p>` : `<p>${json_data['login']} doesn't set name property</p>`
            personal_info += json_data['blog'] ? `<p>${json_data['blog']}</p>` : ``
            personal_info += json_data['location'] ? `<p>${json_data['location']}</p>` : ``
        let bio_data = json_data['bio']
        console.log(interested_language)

        let bio_info = ``
        if (bio_data) {
            let bio_parts = bio_data.split("\n")
            for (let i = 0; i < bio_parts.length; i++) {
                bio_info += `<div>${bio_parts[i]}</div>`
            }
        }
        else {
            bio_info = `<p>${json_data['login']} doesn't set bio property</p>`
        }
        bio_info += interested_language ? `Language Interest: ${interested_language}` : ``
        profile_img_obj.src = json_data['avatar_url']
        personal_info_obj.innerHTML = personal_info
        bio_info_obj.innerHTML = bio_info


        msg_obj.style.color = 'white'
        msg_obj.innerHTML = '<p>Information retrieved</p>'
    }

    console.log(json_data)
}


/*
    Handler of the submit button
    First, get the text written in the textarea and then add it to the api url
    Second, check whether the username that written in the textarea exists in the localStorage or not, if the username
     doesn't exist in the localStorage then it will be gotten from the api and then added to the localStorage after that
      the favorite language of the user will be found by function favorite_language, and finally the HTML page
       will be updated based on the retrieved information
    If any error happen during the fetch time, the appropriate message will be displayed under the submit button
    If the username exists in the localStorage then the user information will be retrieved from localStorage, after that
      the favorite language of the user will be found by function favorite_language, and finally the HTML page will be
       updated based on the retrieved information
 */
async function submit_btn_handler() {
    let text_area_obj = document.getElementById('get_username')
    let username = text_area_obj.value
    let json_response
    myStorage.removeItem('temp')
    myStorage.removeItem('favorite_lang')
    msg_obj.innerHTML = "<div class=\"loader\"></div>\n"
    if (myStorage.getItem(username) === null) {
        console.log('https://api.github.com/users/'+username)
        console.log('fetch')
        let addr = 'https://api.github.com/users/'+username
        fetch(addr)
            .then(response => {
                return response.json();
            })
            .then(async function (data) {
                json_response = JSON.stringify(data)
                myStorage.setItem(username, json_response)
                let result = await favorite_language(data['repos_url'])
                update_info(json_response, result)
            })
            .catch(error => {
                msg_obj.style.color = 'red'
                msg_obj.innerHTML = `<p>Error: Network Error, ${error}</p>`

            });
    }
    else {
        console.log('localStorage')
        json_response = myStorage.getItem(username)
        let result = await favorite_language(JSON.parse(json_response)['repos_url'])
        update_info(json_response, result)
    }

}

// Set the submit_btn_handler as a handler for submit button
btn_obj.onclick = submit_btn_handler
