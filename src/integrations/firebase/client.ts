import { initializeApp } from "firebase/app";
import { getAuth } from "firebase/auth";

const firebaseConfig = {
  apiKey: "AIzaSyBeG87ZLnil7Iz7F8JeeNifuMt1Cf-jc50",
  authDomain: "neuromate-7b7b2.firebaseapp.com",
  projectId: "neuromate-7b7b2",
  storageBucket: "neuromate-7b7b2.appspot.com",
  messagingSenderId: "624769236352",
  appId: "1:624769236352:web:ab83f12c980640f2039565",
  measurementId: "G-N3GVVW8LW0"
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);
export const auth = getAuth(app);
