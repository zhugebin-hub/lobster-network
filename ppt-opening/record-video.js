const puppeteer = require('puppeteer');
const { spawn } = require('child_process');
const path = require('path');
const fs = require('fs');

async function recordVideo() {
    const htmlPath = path.resolve(__dirname, 'matrix-opening.html');
    const outputDir = __dirname;
    const framesDir = path.join(outputDir, 'frames');
    const outputFile = path.join(outputDir, 'matrix-opening.mp4');
    
    // Create frames directory
    if (!fs.existsSync(framesDir)) {
        fs.mkdirSync(framesDir, { recursive: true });
    }
    
    console.log('Starting browser...');
    const browser = await puppeteer.launch({
        headless: 'new',
        args: [
            '--no-sandbox',
            '--disable-setuid-sandbox',
            '--disable-dev-shm-usage',
            '--window-size=1920,1080'
        ]
    });
    
    const page = await browser.newPage();
    await page.setViewport({ width: 1920, height: 1080 });
    
    console.log('Loading HTML file:', htmlPath);
    await page.goto(`file://${htmlPath}`, { waitUntil: 'networkidle0' });
    
    console.log('Recording frames for 10 seconds...');
    const fps = 30;
    const duration = 10;
    const totalFrames = fps * duration;
    
    for (let i = 0; i < totalFrames; i++) {
        await page.screenshot({
            path: path.join(framesDir, `frame_${String(i).padStart(5, '0')}.png`),
            type: 'png'
        });
        await new Promise(resolve => setTimeout(resolve, 1000 / fps));
        
        if (i % 30 === 0) {
            console.log(`Recorded ${i}/${totalFrames} frames...`);
        }
    }
    
    console.log('All frames captured. Converting to video...');
    await browser.close();
    
    // Use ffmpeg to convert frames to video
    return new Promise((resolve, reject) => {
        const ffmpegArgs = [
            '-framerate', '30',
            '-i', path.join(framesDir, 'frame_%05d.png'),
            '-c:v', 'libx264',
            '-pix_fmt', 'yuv420p',
            '-crf', '23',
            '-y',
            outputFile
        ];
        
        const ffmpeg = spawn('ffmpeg', ffmpegArgs);
        
        ffmpeg.stdout.on('data', (data) => {
            console.log(`ffmpeg: ${data}`);
        });
        
        ffmpeg.stderr.on('data', (data) => {
            console.error(`ffmpeg: ${data}`);
        });
        
        ffmpeg.on('close', (code) => {
            if (code === 0) {
                console.log(`Video created successfully: ${outputFile}`);
                // Clean up frames
                fs.rmSync(framesDir, { recursive: true, force: true });
                resolve(outputFile);
            } else {
                reject(new Error(`ffmpeg exited with code ${code}`));
            }
        });
    });
}

recordVideo()
    .then(file => {
        console.log('Done! Video saved to:', file);
        process.exit(0);
    })
    .catch(err => {
        console.error('Error:', err);
        process.exit(1);
    });
