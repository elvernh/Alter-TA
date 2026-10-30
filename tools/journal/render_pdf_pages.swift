import AppKit
import CoreGraphics
import Foundation

guard CommandLine.arguments.count == 5 else {
    fputs("usage: render_pdf_pages.swift input.pdf output_dir dpi prefix\n", stderr)
    exit(2)
}

let inputURL = URL(fileURLWithPath: CommandLine.arguments[1]) as CFURL
let outputDirectory = URL(fileURLWithPath: CommandLine.arguments[2], isDirectory: true)
guard let dpi = Double(CommandLine.arguments[3]), dpi > 0 else {
    fputs("dpi must be positive\n", stderr)
    exit(2)
}
let prefix = CommandLine.arguments[4]

guard let document = CGPDFDocument(inputURL) else {
    fputs("could not open PDF\n", stderr)
    exit(1)
}

for pageNumber in 1...document.numberOfPages {
    guard let page = document.page(at: pageNumber) else { continue }
    let mediaBox = page.getBoxRect(.mediaBox)
    let scale = dpi / 72.0
    let pixelWidth = max(1, Int(ceil(mediaBox.width * scale)))
    let pixelHeight = max(1, Int(ceil(mediaBox.height * scale)))
    let colorSpace = CGColorSpaceCreateDeviceRGB()
    guard let context = CGContext(
        data: nil,
        width: pixelWidth,
        height: pixelHeight,
        bitsPerComponent: 8,
        bytesPerRow: 0,
        space: colorSpace,
        bitmapInfo: CGImageAlphaInfo.premultipliedLast.rawValue
    ) else {
        fputs("could not create image context\n", stderr)
        exit(1)
    }

    context.setFillColor(NSColor.white.cgColor)
    context.fill(CGRect(x: 0, y: 0, width: pixelWidth, height: pixelHeight))
    let target = CGRect(x: 0, y: 0, width: pixelWidth, height: pixelHeight)
    context.concatenate(
        page.getDrawingTransform(
            .mediaBox,
            rect: target,
            rotate: 0,
            preserveAspectRatio: true
        )
    )
    context.drawPDFPage(page)

    guard let image = context.makeImage() else {
        fputs("could not finalize page image\n", stderr)
        exit(1)
    }
    let bitmap = NSBitmapImageRep(cgImage: image)
    guard let pngData = bitmap.representation(using: .png, properties: [:]) else {
        fputs("could not encode PNG\n", stderr)
        exit(1)
    }
    let filename = String(format: "%@0000-%02d.png", prefix, pageNumber)
    let outputURL = outputDirectory.appendingPathComponent(filename)
    try pngData.write(to: outputURL, options: .atomic)
    print(outputURL.path)
}
