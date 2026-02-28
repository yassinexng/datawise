import { createRouter, createWebHistory } from 'vue-router'

import LoginPage from '../pages/LoginPage.vue'
import RegisterPage from '../pages/RegisterPage.vue'
import MainPage from '../pages/MainPage.vue'
import FileUploadPage from '../tabs/FileUpload/FileUploadPage.vue'
import EDA from '../tabs/DataAnalysis/EDA.vue'
import Clean from '../tabs/DataAnalysis/Clean.vue'
import Visualize from '../tabs/DataAnalysis/Visualize.vue'
import ConfirmEmail from '../pages/ConfirmEmail.vue'
import forgetpassword1  from '../pages/forgetpassword1.vue'
import forgetpassword2  from '../pages/forgetpassword2.vue'
import forgetpassword3  from '../pages/forgetpassword3.vue'

const routes = [
    { 
        path: '/login', 
        name: 'Login', 
        component: LoginPage 
    },
    { 
        path: '/register', 
        name: 'Register', 
        component: RegisterPage 
    },
    { 
        path: '/confirmemail', 
        name: 'ConfirmEmail', 
        component: ConfirmEmail 
    },
    { 
        path: '/forgetpassword1', 
        name: 'ForgetPassword1', 
        component: forgetpassword1 
    },
    
    { 
        path: '/forgetpassword2', 
        name: 'ForgetPassword2', 
        component: forgetpassword2 
    },
    { 
        path: '/forgetpassword3', 
        name: 'ForgetPassword3', 
        component: forgetpassword3 
    },
    {
        path: '/mainpage',
        component: MainPage,
        children: [
            { 
                path: 'upload', 
                name: 'FileUpload', 
                component: FileUploadPage 
            },
            {
                path: 'DataAnalysis/EDA',
                name: 'EDA',
                component: EDA
            },
            {
                path: 'DataAnalysis/Clean/:id?',
                name: 'Clean',
                component: Clean
            },
            {
                path: 'DataAnalysis/Visualize/:id?',
                name: 'Visualize',
                component: Visualize
            }
        ]
    }
]

const router = createRouter({
    history: createWebHistory(),
    routes
})

export default router