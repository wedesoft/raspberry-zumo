require_relative '../service'


describe Service do
  let(:udp_server) { double 'udp_server' }
  let(:gpio) { double 'gpio' }

  before :each do
    allow(GPIO).to receive(:new).and_return gpio
    allow(UDPServer).to receive(:new).and_return udp_server
    allow(udp_server).to receive(:read).and_return "0,0"
    allow(gpio).to receive :update
  end

  describe :initialize do
    it 'should initialize general purpose input/output' do
      expect(GPIO).to receive :new
      Service.new
    end

    it 'should initialize the UDP server' do
      expect(UDPServer).to receive :new
      Service.new
    end
  end

  describe :update do
    it 'should receive UDP packets' do
      expect(udp_server).to receive :read
      Service.new.update
    end

    it 'should update the drives' do
      expect(gpio).to receive(:update).with 0, 0, 0, 0
      Service.new.update
    end

    it 'should drive forward' do
      allow(udp_server).to receive(:read).and_return "-32767,-32767"
      expect(gpio).to receive(:update).with 0, 100, 0, 100
      Service.new.update
    end

    it 'should drive backward' do
      allow(udp_server).to receive(:read).and_return "32767,32767"
      expect(gpio).to receive(:update).with 100, 0, 100, 0
      Service.new.update
    end

    it 'should drive left' do
      allow(udp_server).to receive(:read).and_return "32767,-32767"
      expect(gpio).to receive(:update).with 100, 0, 0, 100
      Service.new.update
    end

    it 'should ignore small values' do
      allow(udp_server).to receive(:read).and_return "#{Service::DEADZONE},#{-Service::DEADZONE}"
      expect(gpio).to receive(:update).with 0, 0, 0, 0
      Service.new.update
    end

    it 'should not exceed 100.0' do
      allow(udp_server).to receive(:read).and_return "32768,-32768"
      expect(gpio).to receive(:update).with 100, 0, 0, 100
      Service.new.update
    end
  end

  describe :stop do
    it 'should stop the general purpose input/output' do
      expect(gpio).to receive(:stop)
      Service.new.stop
    end
  end
end
