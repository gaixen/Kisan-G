const express = require('express');
const router = express.Router();
const axios = require('axios');

const GEMINI_API_URL = "https://ai.google.dev/gemma/docs/gemma-3n"
const GEMINI_API_KEY = process.env.GEMINI_API_KEY;

router.post('/', async (req, res) => {
    const {question} = req.body;
    if (!question) return res.status(400).json({error: "Question is required"});

    try {
        const response = await axios.post('${GEMINI_API_URL} ? key = $ {GEMINI_API_KEY}',
            {
                contents: [{ parts: [{test: question}]}]
            }
        );

        const answer = response.data?.candidates?.[0]?.content?.parts?.[0]?.text || response.data?.candidates?.[0]?.output || "I'm sorry, I don't know the answer to that question.";

        res.json({answer});
    } catch(e) {
        console.error(e.response?.data || e.message);
        res.status(500).json({error: "An error occurred while processing the question."});
    }
});

module.exports = router;