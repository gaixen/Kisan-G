import axios from 'axios';
import { FaQuestion } from 'react-icons/fa';

export const askGemini = async (question : string) => {
    const {data} = await axios.get('api/ask-gemini', {question = question});
    return data.answer;
}