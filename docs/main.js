"use strict";
// References derived from docs/computer_vision_pipeline_texts.md
const texts = [
    {
        reference: 'Richard Szeliski, Computer Vision: Algorithms and Applications, 2nd ed., Springer, 2022.',
        description: 'Comprehensive textbook covering modern computer vision techniques with emphasis on practical algorithms.',
    },
    {
        reference: 'Richard Hartley and Andrew Zisserman, Multiple View Geometry in Computer Vision, 2nd ed., Cambridge University Press, 2004.',
        description: 'Authoritative treatment of geometric methods for reconstructing 3-D scenes from multiple images.',
    },
    {
        reference: 'Rafael C. Gonzalez and Richard E. Woods, Digital Image Processing, 4th ed., Pearson, 2018.',
        description: 'Classic reference on image fundamentals, filtering, and enhancement techniques.',
    },
    {
        reference: 'Ian Goodfellow, Yoshua Bengio, and Aaron Courville, Deep Learning, MIT Press, 2016.',
        description: 'Provides the theoretical basis for deep neural networks that power modern vision systems.',
    },
    {
        reference: 'Adrian Kaehler and Gary Bradski, Learning OpenCV 4: Computer Vision with Python, O\'Reilly Media, 2019.',
        description: 'Practical guide to building vision applications using the OpenCV library.',
    },
    {
        reference: 'Alan C. Bovik (ed.), The Essential Guide to Video Processing, 2nd ed., Academic Press, 2009.',
        description: 'Covers video processing pipelines, including motion estimation, compression, and display.',
    },
    {
        reference: 'Martin Kleppmann, Designing Data-Intensive Applications, O\'Reilly Media, 2017.',
        description: 'Explores principles for building reliable, scalable data pipelines and distributed systems.',
    },
    {
        reference: 'Tyler Akidau, Slava Chernyak, and Reuven Lax, Streaming Systems, O\'Reilly Media, 2018.',
        description: 'Introduces concepts and architectures for real-time data processing pipelines.',
    },
    {
        reference: 'James Densmore, Data Pipelines Pocket Reference, O\'Reilly Media, 2021.',
        description: 'Concise patterns and best practices for designing production data pipelines.',
    },
    {
        reference: 'Hannes Hapke and Catherine Nelson, Building Machine Learning Pipelines, O\'Reilly Media, 2020.',
        description: 'Hands-on guide to constructing end-to-end ML pipelines including data ingestion and model deployment.',
    },
];
document.addEventListener('DOMContentLoaded', () => {
    const app = document.getElementById('app');
    if (!app)
        return;
    app.textContent = '';
    const heading = document.createElement('h1');
    heading.textContent = 'Top Texts on Computer Vision and Pipeline Architectures';
    app.appendChild(heading);
    const list = document.createElement('ol');
    texts.forEach(({ reference, description }) => {
        const item = document.createElement('li');
        const refPara = document.createElement('p');
        refPara.textContent = reference;
        item.appendChild(refPara);
        const descPara = document.createElement('p');
        descPara.textContent = description;
        item.appendChild(descPara);
        list.appendChild(item);
    });
    app.appendChild(list);
});
